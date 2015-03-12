from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from lego.app.events.models import Event
from lego.app.events.permissions import EventPermissions
from lego.app.events.serializers import *
from lego.permissions.filters import ObjectPermissionsFilter


class EventViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return EventCreateAndUpdateSerializer
        return EventReadSerializer

    queryset = Event.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (EventPermissions,)
