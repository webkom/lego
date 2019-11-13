from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import decorators, filters, mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from celery import chain

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
from lego.apps.events.serializers.events import (
    EventAdministrateSerializer,
    EventCreateAndUpdateSerializer,
    EventReadAuthUserDetailedSerializer,
    EventReadSerializer,
    EventReadUserDetailedSerializer,
    EventUserRegSerializer,
    populate_event_registration_users_with_grade,
)
from lego.apps.events.serializers.pools import PoolCreateAndUpdateSerializer
from lego.apps.events.serializers.registrations import (
    AdminRegistrationCreateAndUpdateSerializer,
    AdminUnregisterSerializer,
    RegistrationConsentSerializer,
    RegistrationCreateAndUpdateSerializer,
    RegistrationPaymentReadSerializer,
    RegistrationReadDetailedSerializer,
    RegistrationReadSerializer,
    RegistrationSearchReadSerializer,
    RegistrationSearchSerializer,
    StripePaymentIntentSerializer,
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
from lego.apps.permissions.api.filters import LegoPermissionFilter
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.users.models import User
from lego.utils.functions import verify_captcha


class EventViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    filter_class = EventsFilterSet
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        LegoPermissionFilter,
    )
    ordering_fields = ("start_time", "end_time", "title")
    ordering = "start_time"
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if self.action in ["list", "upcoming"]:
            queryset = Event.objects.select_related("company").prefetch_related(
                "pools", "pools__registrations", "tags"
            )
        elif self.action == "retrieve":
            queryset = Event.objects.select_related(
                "company", "responsible_group"
            ).prefetch_related("pools", "pools__permission_groups", "tags")
            if user and user.is_authenticated:
                reg_queryset = self.get_registrations(user)
                queryset = queryset.prefetch_related(
                    "can_edit_users",
                    "can_edit_groups",
                    Prefetch("pools__registrations", queryset=reg_queryset),
                    Prefetch("registrations", queryset=reg_queryset),
                )
        else:
            queryset = Event.objects.all()
        return queryset

    def get_registrations(self, user):
        current_user_groups = user.all_groups
        query = Q()
        for group in current_user_groups:
            query |= Q(user__abakus_groups=group)
        registrations = Registration.objects.select_related("user").annotate(
            shared_memberships=Count("user__abakus_groups", filter=query)
        )
        return registrations

    def user_should_see_regs(self, event, user):
        return (
            event.get_possible_pools(user, future=True, is_admitted=False).exists()
            or user.is_abakom_member
            or event.created_by.id == user.id
        )

    def get_serializer_class(self):
        if self.action in ["create", "partial_update", "update"]:
            return EventCreateAndUpdateSerializer
        if self.action == "list":
            return EventReadSerializer
        if self.action == "retrieve":
            user = self.request.user
            event = Event.objects.get(id=self.kwargs.get("pk", None))
            if (
                event
                and user
                and user.is_authenticated
                and self.user_should_see_regs(event, user)
            ):
                return EventReadAuthUserDetailedSerializer
            return EventReadUserDetailedSerializer

        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        """ If the capacity of the event increases we have to bump waiting users. """
        try:
            event_id = self.kwargs.get("pk", None)
            instance = super().update(request, *args, **kwargs)
            check_for_bump_on_pool_creation_or_expansion.delay(event_id)
            return instance
        except RegistrationsExistInPool:
            raise APIRegistrationsExistsInPool()

    def perform_update(self, serializer):
        """
        We set the is_ready flag on update to lock the event for bumping waiting registrations.
        This is_ready flag is set to True when the bumping is finished
        """
        serializer.save(is_ready=False)

    @decorators.action(
        detail=True, methods=["GET"], serializer_class=EventAdministrateSerializer
    )
    def administrate(self, request, *args, **kwargs):
        event_id = self.kwargs.get("pk", None)
        queryset = Event.objects.filter(pk=event_id).prefetch_related(
            "pools__permission_groups",
            Prefetch(
                "pools__registrations",
                queryset=Registration.objects.select_related("user").prefetch_related(
                    "user__abakus_groups"
                ),
            ),
            Prefetch(
                "registrations", queryset=Registration.objects.select_related("user")
            ),
        )
        event = queryset.first()
        event_data = self.get_serializer(event).data
        event_data = populate_event_registration_users_with_grade(event_data)
        return Response(event_data)

    @decorators.action(detail=True, methods=["POST"], serializer_class=BaseSerializer)
    def payment(self, request, *args, **kwargs):
        event_id = self.kwargs.get("pk", None)
        event = Event.objects.get(id=event_id)
        registration = event.get_registration(request.user)

        if not event.is_priced or not event.use_stripe:
            raise APIEventNotPriced()

        if registration is None or not registration.can_pay:
            raise APIPaymentDenied

        if registration.has_paid():
            raise APIPaymentExists()

        if registration.payment_intent_id is None:
            # If the payment_intent was not created when registering
            chain(
                async_initiate_payment.s(registration.id),
                save_and_notify_payment.s(registration.id),
            ).delay()
        else:
            async_retrieve_payment.s(registration.id).delay()

        payment_serializer = RegistrationPaymentReadSerializer(
            registration, context={"request": request}
        )

        response_data = payment_serializer.data

        return Response(data=response_data, status=status.HTTP_202_ACCEPTED)

    @decorators.action(
        detail=False,
        serializer_class=EventUserRegSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def previous(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                registrations__status=constants.SUCCESS_REGISTER,
                registrations__user=request.user,
                start_time__lt=timezone.now(),
            )
            .prefetch_related(
                Prefetch(
                    "registrations",
                    queryset=Registration.objects.filter(
                        user=request.user
                    ).select_related("user", "pool"),
                    to_attr="user_reg",
                ),
                Prefetch(
                    "pools",
                    queryset=Pool.objects.filter(
                        permission_groups__in=self.request.user.all_groups
                    ),
                    to_attr="possible_pools",
                ),
            )
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.action(
        detail=False,
        serializer_class=EventUserRegSerializer,
        permission_classes=[permissions.IsAuthenticated],
    )
    def upcoming(self, request):
        queryset = (
            self.get_queryset()
            .filter(
                registrations__status=constants.SUCCESS_REGISTER,
                registrations__user=request.user,
                start_time__gt=timezone.now(),
            )
            .prefetch_related(
                Prefetch(
                    "registrations",
                    queryset=Registration.objects.filter(
                        user=request.user
                    ).select_related("user", "pool"),
                    to_attr="user_reg",
                ),
                Prefetch(
                    "pools",
                    queryset=Pool.objects.filter(
                        permission_groups__in=self.request.user.all_groups
                    ),
                    to_attr="possible_pools",
                ),
            )
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PoolViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Pool.objects.all()
    serializer_class = PoolCreateAndUpdateSerializer

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk", None)
        return Pool.objects.filter(event=event_id).prefetch_related(
            "permission_groups", "registrations"
        )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValueError:
            raise APIRegistrationsExistsInPool


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
        if event.use_captcha and not verify_captcha(
            serializer.data.get("captcha_response", None)
        ):
            raise ValidationError({"error": "Bad captcha"})

        current_user = request.user

        with transaction.atomic():
            registration = Registration.objects.get_or_create(
                event_id=event_id,
                user_id=current_user.id,
                defaults={"updated_by": current_user, "created_by": current_user},
            )[0]
            feedback = serializer.data.get("feedback", "")
            if registration.event.feedback_required and not feedback:
                raise ValidationError({"error": "Feedback is required"})
            registration.status = constants.PENDING_REGISTER
            registration.feedback = feedback
            registration.save(current_user=current_user)
            transaction.on_commit(lambda: async_register.delay(registration.id))
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
            serializer.validated_data.get("payment_status", None)
            == constants.PAYMENT_MANUAL
        ):
            async_cancel_payment.s(registration.id).delay()

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
        except Event.DoesNotExist:
            raise APIEventNotFound()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registration = event.admin_register(
                admin_user=admin_user, **serializer.validated_data
            )
        except NoSuchPool:
            raise APINoSuchPool()
        except RegistrationExists:
            raise APIRegistrationExists()
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
                async_cancel_payment.s(registration.id).delay()
        except NoSuchRegistration:
            raise APINoSuchRegistration()
        except RegistrationExists:
            raise APIRegistrationExists()
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError(
                {
                    "error": f"There is no user with username {username}",
                    "error_code": "no_user",
                }
            )

        try:
            reg = self.get_queryset().get(user=user)
        except Registration.DoesNotExist:
            raise ValidationError(
                {
                    "error": "The registration does not exist",
                    "error_code": "not_registered",
                }
            )

        if not get_permission_handler(Event).has_perm(
            request.user, "EDIT", obj=reg.event
        ):
            raise PermissionDenied()

        if reg.status != constants.SUCCESS_REGISTER:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is _not_ properly registerd. "
                    f"The registration status for the user is: {reg.status}",
                    "error_code": "already_present",
                }
            )

        if reg.pool is None:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is on the waiting list... "
                    "You can set the presence manualy on the 'Påmeldinger' tab",
                    "error_code": "already_present",
                }
            )

        if reg.presence != constants.UNKNOWN:
            raise ValidationError(
                {
                    "error": f"User {reg.user.username} is already present.",
                    "error_code": "already_present",
                }
            )

        reg.presence = constants.PRESENT
        reg.save()
        data = RegistrationSearchReadSerializer(reg).data
        return Response(data=data, status=status.HTTP_200_OK)


class RegistrationConsentViewSet(
    AllowedPermissionsMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    serializer_class = RegistrationConsentSerializer
    ordering = "registration_date"

    def get_queryset(self):
        event_id = self.kwargs.get("event_pk", None)
        return Registration.objects.filter(event=event_id).prefetch_related("user")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data["username"]
        photo_consent = serializer.data["photo_consent"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError(
                {
                    "error": f"There is no user with username {username}",
                    "error_code": "no_user",
                }
            )

        try:
            reg = self.get_queryset().get(user=user)
        except Registration.DoesNotExist:
            raise ValidationError(
                {
                    "error": "The registration does not exist",
                    "error_code": "not_registered",
                }
            )

        if not get_permission_handler(Event).has_perm(
            request.user, "EDIT", obj=reg.event
        ):
            raise PermissionDenied()

        reg.photo_consent = photo_consent
        reg.save()
        data = RegistrationSearchReadSerializer(reg).data
        return Response(data=data, status=status.HTTP_200_OK)
