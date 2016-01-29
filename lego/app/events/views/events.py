from rest_framework import viewsets

from lego.app.events.models import Event, Pool, Registration
from lego.app.events.permissions import EventPermissions, NestedEventPermissions
from lego.app.events.serializers import (EventCreateAndUpdateSerializer, EventReadSerializer,
                                         PoolSerializer, RegistrationCreateAndUpdateSerializer,
                                         SpecificRegistrationCreateAndUpdateSerializer)
from lego.permissions.filters import ObjectPermissionsFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().prefetch_related('pools__permission_groups')
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return EventCreateAndUpdateSerializer
        return EventReadSerializer


class PoolViewSet(viewsets.ModelViewSet):
    serializer_class = PoolSerializer
    queryset = Pool.objects.all().prefetch_related('permission_groups', 'registrations')
    permission_classes = (NestedEventPermissions,)


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    permission_classes = (NestedEventPermissions,)

    def get_serializer_class(self):
        pool_id = self.kwargs.get('parent_lookup_pool', None)
        if pool_id:
            return SpecificRegistrationCreateAndUpdateSerializer
        else:
            return RegistrationCreateAndUpdateSerializer
