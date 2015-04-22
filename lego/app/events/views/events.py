from rest_framework import viewsets

from lego.app.events.models import Event
from lego.app.events.permissions import EventPermissions
from lego.app.events.serializers import EventSerializer
from lego.permissions.filters import ObjectPermissionsFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)
