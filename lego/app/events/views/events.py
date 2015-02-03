from rest_framework import viewsets

from lego.app.events.models import Event
from lego.app.events.serializers import EventSerializer
from lego.permissions.filters import ObjectPermissionsFilter
from lego.permissions.model_permissions import PostModelPermissions
from lego.permissions.object_permissions import ObjectPermissions


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (PostModelPermissions, ObjectPermissions)
