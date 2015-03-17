from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from lego.app.events.models import Event
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

    @detail_route(methods=['POST'], url_path='pools')
    def add_pool(self, request, pk=None):
        event = self.get_object()
        serializer = PoolSerializer(data=request.data)
        if serializer.is_valid():
            event.add_pool(serializer.data['name'], serializer.data['capacity'],
                           serializer.data['activation_date'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
