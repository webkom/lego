from celery import chain
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import decorators, filters, mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from lego.apps.events import constants
from lego.apps.events.exceptions import (APINoSuchPool, APIPaymentExists,
                                         APIRegistrationsExistsInPool, NoSuchPool,
                                         RegistrationsExistInPool)
from lego.apps.events.filters import EventsFilterSet
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.permissions import (AdministratePermissions, AdminRegistrationPermissions,
                                          PoolPermissions, RegistrationPermissions)
from lego.apps.events.serializers.events import (EventAdministrateSerializer,
                                                 EventCreateAndUpdateSerializer,
                                                 EventReadDetailedSerializer, EventReadSerializer)
from lego.apps.events.serializers.pools import PoolCreateAndUpdateSerializer
from lego.apps.events.serializers.registrations import (AdminRegistrationCreateAndUpdateSerializer,
                                                        RegistrationCreateAndUpdateSerializer,
                                                        RegistrationPaymentReadSerializer,
                                                        RegistrationReadDetailedSerializer,
                                                        RegistrationReadSerializer,
                                                        StripeTokenSerializer)
from lego.apps.events.tasks import (async_payment, async_register, async_unregister,
                                    registration_save)
from lego.apps.permissions.filters import AbakusObjectPermissionFilter
from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.utils.functions import verify_captcha


class EventViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = EventsFilterSet
    ordering = 'start_time'

    def get_queryset(self):
        if self.action == 'list':
            queryset = Event.objects.prefetch_related(
                'pools', 'pools__registrations', 'company', 'tags'
            )
        elif self.action == 'retrieve':
            queryset = Event.objects.prefetch_related(
                'pools', 'pools__permission_groups',
                Prefetch(
                    'pools__registrations', queryset=Registration.objects.select_related('user')
                ),
                Prefetch('registrations', queryset=Registration.objects.select_related('user')),
                'tags'
            )
        else:
            queryset = Event.objects.all()
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return EventCreateAndUpdateSerializer
        if self.action == 'list':
            return EventReadSerializer
        if self.action == 'retrieve':
            return EventReadDetailedSerializer

        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except RegistrationsExistInPool:
            raise APIRegistrationsExistsInPool()

    @decorators.detail_route(
        methods=['GET'], serializer_class=EventAdministrateSerializer,
        permission_classes=(AdministratePermissions,)
    )
    def administrate(self, request, *args, **kwargs):
        event_id = self.kwargs.get('pk', None)
        queryset = Event.objects.filter(pk=event_id).prefetch_related(
            'pools', 'pools__permission_groups',
            Prefetch('pools__registrations', queryset=Registration.objects.select_related('user')),
            Prefetch('registrations', queryset=Registration.objects.select_related('user')),
        )
        serializer = self.get_serializer(queryset.first())
        return Response(serializer.data)

    @decorators.detail_route(methods=['POST'], serializer_class=StripeTokenSerializer)
    def payment(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = self.kwargs.get('pk', None)
        event = Event.objects.get(id=event_id)
        registration = event.get_registration(request.user)

        if not event.is_priced or not event.use_stripe:
            raise PermissionDenied()

        if registration.charge_id:
            raise APIPaymentExists()
        registration.charge_status = constants.PAYMENT_PENDING
        registration.save()
        chain(
            async_payment.s(registration.id, serializer.data['token']),
            registration_save.s(registration.id)
        ).delay()
        payment_serializer = RegistrationPaymentReadSerializer(
            registration, context={'request': request}
        )
        return Response(data=payment_serializer.data, status=status.HTTP_202_ACCEPTED)


class PoolViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Pool.objects.all()
    permission_classes = (PoolPermissions,)
    serializer_class = PoolCreateAndUpdateSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        return Pool.objects.filter(event=event_id).prefetch_related(
            'permission_groups', 'registrations'
        )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ValueError:
            raise APIRegistrationsExistsInPool


class RegistrationViewSet(AllowedPermissionsMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = RegistrationReadSerializer
    permission_classes = (RegistrationPermissions,)
    ordering = 'registration_date'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RegistrationCreateAndUpdateSerializer
        if self.action == 'retrieve':
            return RegistrationReadDetailedSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        return Registration.objects.filter(event=event_id).prefetch_related('user')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = self.kwargs.get('event_pk', None)
        event = Event.objects.get(id=event_id)
        if event.use_captcha and not verify_captcha(serializer.data.get('captcha_response', None)):
            raise ValidationError({'error': 'Bad captcha'})

        user_id = request.user.id

        with transaction.atomic():
            registration = Registration.objects.get_or_create(event_id=event_id, user_id=user_id)[0]
            feedback = serializer.data.get('feedback', '')
            if registration.event.feedback_required and not feedback:
                raise ValidationError({'error': 'Feedback is required'})
            registration.feedback = feedback
            registration.save()
            transaction.on_commit(lambda: async_register.delay(registration.id))
        registration_serializer = RegistrationReadSerializer(registration)
        return Response(data=registration_serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            instance.status = constants.PENDING_UNREGISTER
            instance.save()
            transaction.on_commit(lambda: async_unregister.delay(instance.id))
        serializer = RegistrationReadSerializer(instance)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)

    @decorators.list_route(methods=['POST'],
                           serializer_class=AdminRegistrationCreateAndUpdateSerializer,
                           permission_classes=(AdminRegistrationPermissions,))
    def admin_register(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_pk', None)
        event = Event.objects.get(id=event_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registration = event.admin_register(**serializer.validated_data)
        except NoSuchPool:
            raise APINoSuchPool()
        reg_data = RegistrationReadDetailedSerializer(registration).data
        return Response(data=reg_data, status=status.HTTP_201_CREATED)
