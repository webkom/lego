from lego.app.events.permissions import EventPermissions
from rest_any_permissions.permissions import AnyPermissions
from rest_framework import viewsets

from lego.app.events.models import Event
from lego.app.events.serializers import EventSerializer
from lego.permissions.filters import ObjectPermissionsFilter
from lego.permissions.object_permissions import ObjectPermissions


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (AnyPermissions,)
    any_permission_classes = (EventPermissions, )
