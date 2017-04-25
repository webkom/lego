from rest_framework import decorators, permissions, viewsets
from rest_framework.response import Response

from lego.apps.notifications import constants

from .models import NotificationSetting
from .serializers import NotificationSettingCreateSerializer, NotificationSettingSerializer


class NotificationSettingsViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):

    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return NotificationSetting.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationSettingCreateSerializer
        return NotificationSettingSerializer

    def create(self, request):
        """
        Lookup or create a new settings object and save it with the provided parameters.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_type = serializer.validated_data['notification_type']
        instance, _ = NotificationSetting.lookup_setting(request.user, notification_type)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @decorators.list_route(methods=['GET'])
    def alternatives(self, request):
        """
        Return a list of all possible notification_types and channels.
        """
        return Response({
            'notification_types': constants.NOTIFICATION_TYPES,
            'channels': constants.CHANNELS
        })
