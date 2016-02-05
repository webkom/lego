from rest_framework import viewsets

from lego.app.events.models import Event, Pool, Registration
from lego.app.events.permissions import EventPermissions, NestedEventPermissions
from lego.app.events.serializers import (EventCreateAndUpdateSerializer,
                                         EventReadDetailedSerializer, EventReadSerializer,
                                         PoolCreateAndUpdateSerializer, PoolReadSerializer,
                                         RegistrationCreateAndUpdateSerializer,
                                         SpecificRegistrationCreateAndUpdateSerializer)
from lego.permissions.filters import ObjectPermissionsFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.prefetch_related('pools__permission_groups', 'pools__registrations')
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return EventCreateAndUpdateSerializer

        event_id = self.kwargs.get('pk', None)
        if event_id:
            return EventReadDetailedSerializer

        return EventReadSerializer


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


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    permission_classes = (NestedEventPermissions,)

    def get_serializer_class(self):
        pool_id = self.kwargs.get('pool_pk', None)
        if pool_id:
            return SpecificRegistrationCreateAndUpdateSerializer
        else:
            return RegistrationCreateAndUpdateSerializer

    def get_queryset(self):
        pool_id = self.kwargs.get('pool_pk', None)
        event_id = self.kwargs.get('event_pk', None)
        if pool_id and event_id:
            return Registration.objects.filter(event=event_id, pool=pool_id)
        elif event_id:
            return Registration.objects.filter(event=event_id)
