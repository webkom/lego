from rest_framework import filters, viewsets

from lego.apps.events.filters import EventsFilterSet
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.permissions import NestedEventPermissions
from lego.apps.events.serializers import (EventCreateAndUpdateSerializer,
                                          EventReadDetailedSerializer, EventReadSerializer,
                                          PoolCreateAndUpdateSerializer, PoolReadSerializer,
                                          RegistrationCreateAndUpdateSerializer)
from lego.apps.permissions.filters import AbakusObjectPermissionFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.prefetch_related('pools__permission_groups',
                                              'pools__registrations',
                                              'pools__registrations__user',
                                              'can_view_groups',
                                              'comments')
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = EventsFilterSet

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
    permission_classes = (NestedEventPermissions,)
    serializer_class = RegistrationCreateAndUpdateSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        return Registration.objects.filter(event=event_id, unregistration_date=None)

    def perform_destroy(self, instance):
        instance.event.unregister(instance.user)
