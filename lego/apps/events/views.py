import stripe
from django.db import transaction
from rest_framework import decorators, filters, mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from lego.apps.events import constants
from lego.apps.events.exceptions import NoSuchPool, PaymentExists
from lego.apps.events.filters import EventsFilterSet
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.permissions import NestedEventPermissions
from lego.apps.events.serializers import (AdminRegistrationCreateAndUpdateSerializer,
                                          EventCreateAndUpdateSerializer,
                                          EventReadDetailedSerializer, EventReadSerializer,
                                          PoolCreateAndUpdateSerializer, PoolReadSerializer,
                                          RegistrationCreateAndUpdateSerializer,
                                          RegistrationReadSerializer, StripeTokenSerializer)
from lego.apps.events.tasks import async_register, async_unregister
from lego.apps.permissions.filters import AbakusObjectPermissionFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.prefetch_related('pools__permission_groups',
                                              'pools__registrations',
                                              'pools__registrations__user',
                                              'can_view_groups',
                                              'comments')
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = EventsFilterSet
    ordering = 'start_time'

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'update']:
            return EventCreateAndUpdateSerializer
        if self.action == 'list':
            return EventReadSerializer
        if self.action == 'retrieve':
            return EventReadDetailedSerializer

        return super().get_serializer_class()

    @decorators.detail_route(methods=['POST'], serializer_class=StripeTokenSerializer)
    def payment(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = self.kwargs.get('pk', None)
        event = Event.objects.get(id=event_id)
        registration = event.registrations.get(user=request.user)

        if not registration.pool or not event.is_priced:
            raise PermissionDenied()

        if registration.charge_id:
            raise PaymentExists()

        try:
            response = stripe.Charge.create(
                amount=event.get_price(registration.user),
                currency='NOK',
                source=serializer.data['token'],
                description=event.slug,
                metadata={
                    'EVENT_ID': event_id,
                    'USER': registration.user.full_name,
                    'EMAIL': registration.user.email
                }
            )
            registration.charge_id = response.id
            registration.charge_amount = response.amount
            registration.charge_status = response.status
            registration.save()
            return Response(data=response, status=status.HTTP_200_OK)
        except stripe.error.CardError:
            raise ValidationError({'error': 'Card declined'})
        except stripe.error.InvalidRequestError:
            raise ValidationError({'error': 'Invalid request'})


class PoolViewSet(viewsets.ModelViewSet):
    queryset = Pool.objects.all()
    permission_classes = (NestedEventPermissions,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return PoolCreateAndUpdateSerializer
        return PoolReadSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        if event_id:
            return Pool.objects.filter(event=event_id).prefetch_related('permission_groups',
                                                                        'registrations')


class RegistrationViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    permission_classes = (NestedEventPermissions,)
    serializer_class = RegistrationReadSerializer
    ordering = 'registration_date'

    def get_serializer_class(self):
        if self.action == 'create':
            return RegistrationCreateAndUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        return Registration.objects.filter(event=event_id,
                                           unregistration_date=None).prefetch_related('user')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = self.kwargs.get('event_pk', None)
        user_id = request.user.id
        with transaction.atomic():
            registration = Registration.objects.get_or_create(event_id=event_id,
                                                              user_id=user_id)[0]
            registration.status = constants.PENDING_REGISTER
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
                           serializer_class=AdminRegistrationCreateAndUpdateSerializer)
    def admin_register(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_pk', None)
        event = Event.objects.get(id=event_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            registration = event.admin_register(**serializer.validated_data)
        except ValueError:
            raise NoSuchPool()
        reg_data = RegistrationCreateAndUpdateSerializer(registration).data
        return Response(data=reg_data, status=status.HTTP_201_CREATED)
