from rest_framework import filters, viewsets, decorators, status
from rest_framework.response import Response

from lego.apps.events.filters import EventsFilterSet
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.permissions import NestedEventPermissions
from lego.apps.events.serializers import (EventCreateAndUpdateSerializer,
                                          EventReadDetailedSerializer, EventReadSerializer,
                                          PoolCreateAndUpdateSerializer, PoolReadSerializer,
                                          RegistrationCreateAndUpdateSerializer,
                                          AdminRegistrationCreateAndUpdateSerializer)
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

    def get_serializer_class(self):
        pool = self.kwargs.get('pool', None)
        user = self.kwargs.get('user', None)
        if pool and user:
            return AdminRegistrationCreateAndUpdateSerializer
        return RegistrationCreateAndUpdateSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_pk', None)
        return Registration.objects.filter(event=event_id, unregistration_date=None)

    def perform_destroy(self, instance):
        instance.event.unregister(instance.user)

    @decorators.detail_route(methods=['POST'], serializer_class=AdminRegistrationCreateAndUpdateSerializer)
    def admin_register(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = event.admin_register(**serializer.validated_data)
        #send registration in response? how?
        return Response(status=status.HTTP_201_CREATED)
