from rest_framework import viewsets

from lego.app.events.models import Event, Pool
from lego.app.events.permissions import EventPermissions
from lego.app.events.serializers import (EventCreateAndUpdateSerializer, EventReadSerializer,
                                         PoolSerializer)
from lego.permissions.filters import ObjectPermissionsFilter


class EventViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return EventCreateAndUpdateSerializer
        return EventReadSerializer

    queryset = Event.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)


class PoolViewSet(viewsets.ModelViewSet):

    serializer_class = PoolSerializer
    queryset = Pool.objects.all()
    # filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        if event_id:
            return Pool.objects.filter(event=event_id)
        return super(PoolViewSet, self).get_queryset()
