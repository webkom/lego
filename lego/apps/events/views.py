from math import ceil
from typing import Any

from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, filters, mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from celery.canvas import chain

from lego.apps.events import constants
from lego.apps.events.exceptions import (
    APIEventNotFound,
    APIEventNotPriced,
    APINoSuchPool,
    APINoSuchRegistration,
    APIPaymentDenied,
    APIPaymentExists,
    APIRegistrationExists,
    APIRegistrationsExistsInPool,
    NoSuchPool,
    NoSuchRegistration,
    RegistrationExists,
    RegistrationsExistInPool,
)
from lego.apps.events.filters import EventsFilterSet
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.permissions import EventTypePermission
from lego.apps.events.serializers.events import (
    EventAdministrateAllergiesSerializer,
    EventAdministrateSerializer,
    EventCreateAndUpdateSerializer,
    EventReadAuthUserDetailedSerializer,
    EventReadSerializer,
    EventReadUserDetailedSerializer,
    ImageGallerySerializer,
    populate_event_registration_users_with_grade,
)
from lego.apps.events.serializers.pools import PoolCreateAndUpdateSerializer
from lego.apps.events.serializers.registrations import (
    AdminRegistrationCreateAndUpdateSerializer,
    AdminUnregisterSerializer,
    RegistrationCreateAndUpdateSerializer,
    RegistrationPaymentReadSerializer,
    RegistrationReadDetailedSerializer,
    RegistrationReadSerializer,
    RegistrationSearchReadSerializer,
    RegistrationSearchSerializer,
)
from lego.apps.events.tasks import (
    async_cancel_payment,
    async_initiate_payment,
    async_register,
    async_retrieve_payment,
    async_unregister,
    check_for_bump_on_pool_creation_or_expansion,
    save_and_notify_payment,
)
from lego.apps.events.websockets import notify_event_registration
from lego.apps.files.constants import IMAGE
from lego.apps.files.models import File
from lego.apps.permissions.api.filters import LegoPermissionFilter
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT, VIEW
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.users.constants import AUTUMN, SPRING
from lego.apps.users.models import PhotoConsent, User
from lego.utils.functions import request_plausible_statistics, verify_captcha


def get_registration_eligibility(event: Event, user: User) -> dict[str, Any]:
    now = timezone.now()
    registration = event.registrations.filter(user=user).first()

    if registration and registration.status in [
        constants.PENDING_REGISTER,
        constants.SUCCESS_REGISTER,
    ]:
        return {
            "can_register_now": False,
            "is_registration_delayed": False,
            "delay_until": None,
            "delay_seconds": 0,
            "will_be_waiting_list": registration.pool is None,
            "reason": "already_registered",
        }

    if event.registration_close_time < now:
        return {
            "can_register_now": False,
            "is_registration_delayed": False,
            "delay_until": None,
            "delay_seconds": 0,
            "will_be_waiting_list": False,
            "reason": "registration_closed",
        }

    if user.unanswered_surveys():
        return {
            "can_register_now": False,
            "is_registration_delayed": False,
            "delay_until": None,
            "delay_seconds": 0,
            "will_be_waiting_list": False,
            "reason": "unanswered_surveys",
        }

    if not event.is_ready:
        return {
            "can_register_now": False,
            "is_registration_delayed": False,
            "delay_until": None,
            "delay_seconds": 0,
            "will_be_waiting_list": False,
            "reason": "event_not_ready",
        }

    current_semester = AUTUMN if event.start_time.month > 7 else SPRING
    if event.use_consent and not user.has_registered_photo_consents_for_semester(
        event.start_time.year, current_semester
    ):
        return {
            "can_register_now": False,
            "is_registration_delayed": False,
            "delay_until": None,
            "delay_seconds": 0,
            "will_be_waiting_list": False,
            "reason": "missing_photo_consents",
        }

    is_admitted = event.is_admitted(user)
    all_pools = event.pools.all()
    possible_pools_now = event.get_possible_pools(
        user, all_pools=all_pools, is_admitted=is_admitted
    )
    possible_pools_future = event.get_possible_pools(
        user, future=True, all_pools=all_pools, is_admitted=is_admitted
    )

    if not possible_pools_future.exists():
        return {
            "can_register_now": False,
            "is_registration_delayed": False,
            "delay_until": None,
            "delay_seconds": 0,
            "will_be_waiting_list": False,
            "reason": "no_available_pools",
        }

    penalties = user.number_of_penalties() if event.heed_penalties else 0
    earliest_registration_time = event.get_earliest_registration_time(
        user, pools=possible_pools_future, penalties=penalties
    )
    is_registration_delayed = bool(
        earliest_registration_time and earliest_registration_time > now
    )
    delay_seconds = (
        ceil((earliest_registration_time - now).total_seconds())
        if is_registration_delayed
        else 0
    )

    can_register_now = possible_pools_now.exists() and not is_registration_delayed

    pools_for_waiting_list_eval = (
        possible_pools_now if possible_pools_now.exists() else possible_pools_future
    )
    will_be_waiting_list = False
    if penalties >= 3:
        will_be_waiting_list = True
    elif pools_for_waiting_list_eval.count() == 1:
        will_be_waiting_list = pools_for_waiting_list_eval[0].is_full
    elif event.is_merged:
        if possible_pools_now.exists():
            will_be_waiting_list = event.is_full
        else:
            will_be_waiting_list = event.get_is_full(
                queryset=pools_for_waiting_list_eval
            )
    else:
        _, open_pools = event.calculate_full_pools(pools_for_waiting_list_eval)
        will_be_waiting_list = len(open_pools) == 0

    return {
        "can_register_now": can_register_now,
        "is_registration_delayed": is_registration_delayed,
        "delay_until": earliest_registration_time if is_registration_delayed else None,
        "delay_seconds": delay_seconds,
        "will_be_waiting_list": will_be_waiting_list,
        "reason": (
            None
            if can_register_now
            else (
                "registration_delayed"
                if is_registration_delayed
                else "cannot_register_now"
            )
        ),
    }


class EventViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    filterset_class = EventsFilterSet
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        LegoPermissionFilter,
    )
    ordering_fields = ("start_time", "end_time", "title")
    ordering = "start_time"

    permission_classes = [EventTypePermission]

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get("pk")

        try:
            obj = queryset.get(id=pk)
        except (Event.DoesNotExist, ValueError):
            obj = get_object_or_404(queryset, slug=pk)
        # check if user has permission to view the event or return 404
        try:
            self.check_object_permissions(self.request, obj)
        except PermissionDenied:
            raise Http404("Not found") from None
        return obj

    def get_queryset(self):
        if self.request is None:
            return Event.objects.none()

        user = self.request.user
        if self.action in ["list", "upcoming", "previous"]:
            queryset = Event.objects.select_related(
                "company",
            ).prefetch_related(
                "pools",
                "pools__registrations",
                "tags",
                "survey",
            )
            if user.is_authenticated:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        "pools",
                        queryset=Pool.objects.filter(
                            permission_groups__in=self.request.user.all_groups
                        ).distinct(),
                        to_attr="possible_pools",
                    ),
                    Prefetch(
                        "registrations",
                        queryset=Registration.objects.filter(user=user)
                        .exclude(status=constants.SUCCESS_UNREGISTER)
                        .select_related("user", "pool"),
                        to_attr="user_reg",
                    ),
                )
        elif self.action == "retrieve":
            queryset = Event.objects.select_related(
                "company", "responsible_group"
            ).prefetch_related("pools", "pools__permission_groups", "tags", "survey")
            if user and user.is_authenticated:
                reg_queryset = self.get_registrations(user)
                queryset = queryset.prefetch_related(
                    "can_edit_users",
                    "can_edit_groups",
                    Prefetch("pools__registrations", queryset=reg_queryset),
                    Prefetch(
                        "registrations",
                        queryset=Registration.objects.filter(user=user)
                        .exclude(status=constants.SUCCESS_UNREGISTER)
                        .select_related("user", "pool")
                        .prefetch_related("user__abakus_groups"),
                        to_attr="user_reg",
                    ),
                )
        else:
            queryset = Event.objects.all()

        return queryset

    def get_registrations(self, user):
        current_user_groups = user.all_groups
        query = Q()
        for group in current_user_groups:
            query |= Q(user__abakus_groups=group)
        registrations = (
            Registration.objects.select_related("user")
            .prefetch_related("user__abakus_groups")
            .annotate(shared_memberships=Count("user__abakus_groups", filter=query))
        )
        return registrations

    def get_serializer_class(self) -> BaseSerializer:
        if self.action in ["create", "partial_update", "update"]:
            return EventCreateAndUpdateSerializer
        if self.action == "list":
            return EventReadSerializer
        if self.action == "retrieve":
            user: User = self.request.user
            pk = self.kwargs.get("pk", None)
            event = (
                Event.objects.get(id=pk) if pk.isdigit() else Event.objects.get(slug=pk)
            )
            if (
                event
                and user
                and user.is_authenticated
                and event.user_should_see_regs(user)
            ):
                return EventReadAuthUserDetailedSerializer
            return EventReadUserDetailedSerializer

        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        """If the capacity of the event increases we have to bump waiting users."""
        try:
            event_id: int = self.kwargs.get("pk", None)
            instance = super().update(request, *args, **kwargs)
            check_for_bump_on_pool_creation_or_expansion.delay(event_id)
            return instance
        except RegistrationsExistInPool as e:
            raise APIRegistrationsExistsInPool() from e

    def perform_update(self, serializer):
        """
        We set the is_ready flag on update to lock the event for bumping waiting registrations.
        This is_ready flag is set to True when the bumping is finished
        """
        serializer.save(is_ready=False)

    @decorators.action(detail=True, methods=["GET"])
    def administrate(self, request, *args, **kwargs):
        event_id = self.kwargs.get("pk", None)
        serializer = EventAdministrateSerializer
        event = Event.objects.get(pk=event_id)
        queryset = Event.objects.filter(pk=event_id).prefetch_related(
            "pools__permission_groups",
            Prefetch(
                "pools__registrations",
                queryset=Registration.objects.select_related("user").prefetch_related(
                    "user__abakus_groups",
                    Prefetch(
                        "user__photo_consents",
                        queryset=PhotoConsent.objects.filter(
                            year=event.start_time.year,
                            semester=PhotoConsent.get_semester(event.start_time),
                        ),
                    ),
                ),
            ),
            Prefetch(
                "registrations",
                queryset=Registration.objects.select_related("user").prefetch_related(
                    Prefetch(
                        "user__photo_consents",
                        queryset=PhotoConsent.objects.filter(
                            year=event.start_time.year,
                            semester=PhotoConsent.get_semester(event.start_time),
                        ),
                    ),
                ),
            ),
        )
        event = queryset.first()
        event_data = serializer(event, context={"request": request}).data
        event_data = populate_event_registration_users_with_grade(event_data)
        return Response(event_data)

    @decorators.action(detail=True, methods=["GET"])
    def allergies(self, request, *args, **kwargs):
        event_id = self.kwargs.get("pk", None)
        serializer = EventAdministrateSerializer
        event = Event.objects.get(pk=event_id)
        if event.user_should_see_allergies(request.user):
            serializer = EventAdministrateAllergiesSerializer

        event_data = serializer(event).data
        return Response(event_data)

    @decorators.action(detail=True, methods=["GET"])
    def statistics(self, request, *args, **kwargs):
        event_id = self.kwargs.get("pk", None)
        event = Event.objects.get(pk=event_id)

        response = request_plausible_statistics(event)
        return Response(response.json())

    @decorators.action(detail=True, methods=["POST"], serializer_class=BaseSerializer)
    def payment(self, request, *args, **kwargs):
        event_id = self.kwargs.get("pk", None)
        event = Event.objects.get(id=event_id)
        registration = event.get_registration(request.user)

        if not event.is_priced or not event.use_stripe:
            raise APIEventNotPriced()

        if registration is None or not registration.can_pay:
            raise APIPaymentDenied()

        if registration.has_paid():
            raise APIPaymentExists()

        if registration.payment_intent_id is None:
            # If the payment_intent was not created when registering
            chain(
                async_initiate_payment.s(registration.id),
                save_and_notify_payment.s(registration.id),
            ).delay()
        else:
            async_retrieve_payment.delay(registration.id)

        payment_serializer = RegistrationPaymentReadSerializer(
            registration, context={"request": request}
        )

        response_data = payment_serializer.data

        return Response(data=response_data, status=status.HTTP_202_ACCEPTED)

    @decorators.action(
        detail=False,
        serializer_class=EventReadSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def previous(self, request):
        queryset = self.get_queryset().filter(
            registrations__status=constants.SUCCESS_REGISTER,
            registrations__user=request.user,
            start_time__lt=timezone.now(),
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.action(
        detail=False,
        serializer_class=EventReadSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def upcoming(self, request):
        queryset = self.get_queryset().filter(
            registrations__status=constants.SUCCESS_REGISTER,
            registrations__user=request.user,
            start_time__gt=timezone.now(),
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.action(
        detail=False,
        serializer_class=ImageGallerySerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def cover_image_gallery(self, request):
        if request.user.has_perm(EDIT, Event) is False:
            raise PermissionDenied()
        queryset = File.objects.filter(
            file_type=IMAGE,
            save_for_use=True,
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.action(
        detail=True,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="registration-eligibility",
    )
    def registration_eligibility(self, request, *args, **kwargs):
        event = self.get_object()
        if not get_permission_handler(Event).has_perm(request.user, VIEW, obj=event):
            raise PermissionDenied()
        return Response(get_registration_eligibility(event=event, user=request.user))


class PoolViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Pool.objects.all()
    serializer_class = PoolCreateAndUpdateSerializer

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk")
        return Pool.objects.filter(event=event_id).prefetch_related(
            "permission_groups", "registrations"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        event_id = self.kwargs.get("event_pk")
        if event_id:
            context["event"] = get_object_or_404(Event, pk=event_id)
        return context

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValueError as e:
            raise APIRegistrationsExistsInPool from e


class RegistrationViewSet(
    AllowedPermissionsMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RegistrationReadSerializer
    ordering = "registration_date"

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RegistrationCreateAndUpdateSerializer
        if self.action == "retrieve":
            return RegistrationReadDetailedSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk", None)
        return Registration.objects.filter(event=event_id).prefetch_related("user")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = self.kwargs.get("event_pk", None)
        event = Event.objects.get(id=event_id)

        if not get_permission_handler(Event).has_perm(request.user, VIEW, obj=event):
            raise PermissionDenied()

        if event.use_captcha and not verify_captcha(
            serializer.data.get("captcha_response", None)
        ):
            raise ValidationError({"error": "Bad captcha"})

        current_user = request.user

        with transaction.atomic():
            registration, is_new = Registration.objects.get_or_create(
                event_id=event_id,
                user_id=current_user.id,
                defaults={"updated_by": current_user, "created_by": current_user},
            )
            feedback = serializer.data.get("feedback", "")
            if registration.event.feedback_required and not feedback:
                raise ValidationError({"error": "Feedback is required"})
            if not is_new and registration.status in [
                constants.PENDING_REGISTER,
                constants.SUCCESS_REGISTER,
            ]:
                raise APIRegistrationExists(
                    {"error": "User has already requested to register for this event"}
                )
            registration.status = constants.PENDING_REGISTER
            registration.feedback = feedback
            registration.save(current_user=current_user)
            transaction.on_commit(lambda: async_register.delay(registration.id))
        registration.refresh_from_db()
        registration_serializer = RegistrationReadSerializer(
            registration, context={"user": registration.user}
        )
        return Response(
            data=registration_serializer.data, status=status.HTTP_202_ACCEPTED
        )

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            instance.status = constants.PENDING_UNREGISTER
            instance.save()
            transaction.on_commit(lambda: async_unregister.delay(instance.id))
        serializer = RegistrationReadSerializer(instance)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)

    def update(self, request, *args, **kwargs):
        registration = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (
            registration.payment_intent_id
            and serializer.validated_data.get("payment_status", None)
            == constants.PAYMENT_MANUAL
        ):
            async_cancel_payment.delay(registration.id)

        return super().update(request, *args, **kwargs)

    @decorators.action(
        detail=False,
        methods=["POST"],
        serializer_class=AdminRegistrationCreateAndUpdateSerializer,
    )
    def admin_register(self, request, *args, **kwargs):
        admin_user = request.user
        event_id = self.kwargs.get("event_pk", None)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist as e:
            raise APIEventNotFound() from e
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registration = event.admin_register(
                admin_user=admin_user, **serializer.validated_data
            )
            notify_event_registration(
                constants.SOCKET_REGISTRATION_SUCCESS, registration
            )
        except NoSuchPool as e:
            raise APINoSuchPool() from e
        except RegistrationExists as e:
            raise APIRegistrationExists() from e
        reg_data = RegistrationReadDetailedSerializer(registration).data
        return Response(data=reg_data, status=status.HTTP_201_CREATED)

    @decorators.action(
        detail=False, methods=["POST"], serializer_class=AdminUnregisterSerializer
    )
    def admin_unregister(self, request, *args, **kwargs):
        admin_user = request.user
        event_id = self.kwargs.get("event_pk", None)
        event = Event.objects.get(id=event_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registration = event.admin_unregister(
                admin_user=admin_user, **serializer.validated_data
            )
            if (
                registration.payment_intent_id
                and registration.payment_status != constants.PAYMENT_SUCCESS
            ):
                async_cancel_payment.delay(registration.id)
            notify_event_registration(
                constants.SOCKET_UNREGISTRATION_SUCCESS, registration
            )
        except NoSuchRegistration as e:
            raise APINoSuchRegistration() from e
        except RegistrationExists as e:
            raise APIRegistrationExists() from e
        reg_data = RegistrationReadDetailedSerializer(registration).data

        return Response(data=reg_data, status=status.HTTP_200_OK)


class RegistrationSearchViewSet(
    AllowedPermissionsMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = RegistrationSearchSerializer
    ordering = "registration_date"

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk", None)
        return Registration.objects.filter(event=event_id).prefetch_related("user")

    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get("event_pk", None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise ValidationError(
                {
                    "error": f"There is no user with username {username}",
                    "error_code": "no_user",
                }
            ) from e

        try:
            reg = self.get_queryset().get(user=user)
        except Registration.DoesNotExist as e:
            raise ValidationError(
                {
                    "error": "The registration does not exist",
                    "error_code": "not_registered",
                }
            ) from e

        if not get_permission_handler(Event).has_perm(
            request.user, EDIT, obj=reg.event
        ):
            raise PermissionDenied()

        # Registration statuses
        if reg.status == constants.SUCCESS_UNREGISTER:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is unregistered.",
                    "error_code": "unregistered",
                }
            )

        if reg.status != constants.SUCCESS_REGISTER:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is _not_ properly registerd. "
                    f"The registration status for the user is: {reg.status}",
                    "error_code": "not_properly_registered",
                }
            )

        if reg.pool is None:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is on the waiting list... "
                    "You can set the presence manualy on the 'Påmeldinger' tab",
                    "error_code": "waitlisted",
                }
            )

        # Registration presences
        if reg.presence == constants.PRESENCE_CHOICES.PRESENT:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is already present.",
                    "error_code": "already_present",
                }
            )

        if reg.presence != constants.PRESENCE_CHOICES.UNKNOWN:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is late or absent.",
                    "error_code": "late_or_absent",
                }
            )

        # Payment status
        event = Event.objects.get(pk=event_id)
        if (
            event.is_priced
            and reg.payment_status != constants.PAYMENT_SUCCESS
            and reg.payment_status != constants.PAYMENT_MANUAL
        ):
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} has not paid.",
                    "error_code": "missing_payment",
                }
            )

        reg.presence = constants.PRESENCE_CHOICES.PRESENT
        reg.save()
        data = RegistrationSearchReadSerializer(reg).data
        return Response(data=data, status=status.HTTP_200_OK)
