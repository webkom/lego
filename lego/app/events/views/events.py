from rest_framework import viewsets

from lego.app.events.models import Event, Pool, Registration
from lego.app.events.permissions import EventPermissions, NestedEventPermissions
from lego.app.events.serializers import (EventCreateAndUpdateSerializer, EventReadSerializer,
                                         PoolSerializer, RegistrationCreateAndUpdateSerializer)
from lego.permissions.filters import ObjectPermissionsFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return EventCreateAndUpdateSerializer
        return EventReadSerializer


class PoolViewSet(viewsets.ModelViewSet):
    serializer_class = PoolSerializer
    queryset = Pool.objects.all()
    permission_classes = (NestedEventPermissions,)

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        if event_id:
            return Pool.objects.filter(event=event_id)


class RegistrationViewSet(viewsets.ModelViewSet):

    serializer_class = RegistrationCreateAndUpdateSerializer
    queryset = Registration.objects.all()
    permission_classes = (NestedEventPermissions,)

    def get_queryset(self):
        pool_id = self.kwargs.get('pool_pk', None)
        event_id = self.kwargs.get('event_pk', None)
        if pool_id and event_id:
            return Registration.objects.filter(event=event_id, pool=pool_id)
