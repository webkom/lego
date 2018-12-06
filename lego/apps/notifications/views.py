from rest_framework import decorators, exceptions, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.notifications import constants
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.stats.utils import track
from push_notifications.api.rest_framework import (
    APNSDeviceAuthorizedViewSet,
    GCMDeviceAuthorizedViewSet,
)

from .models import Announcement, NotificationSetting
from .serializers import (
    AnnouncementDetailSerializer,
    AnnouncementListSerializer,
    NotificationSettingCreateSerializer,
    NotificationSettingSerializer,
)


class NotificationSettingsViewSet(
    viewsets.mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    Manage the notification channels to the authenticated users.
    The default is to send all notifications on all channels.

    list:
    List all existing settings.
    """

    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        return NotificationSetting.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return NotificationSettingCreateSerializer
        return NotificationSettingSerializer

    def create(self, request):
        """
        Lookup or create a new settings object and save it with the provided parameters.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_type = serializer.validated_data["notification_type"]
        instance, _ = NotificationSetting.lookup_setting(
            request.user, notification_type
        )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @decorators.action(detail=False, methods=["GET"])
    def alternatives(self, request):
        """
        Return a list of all possible notification_types and channels.
        """
        return Response(
            {
                "notification_types": constants.NOTIFICATION_TYPES,
                "channels": constants.CHANNELS,
            }
        )


class APNSDeviceViewSet(APNSDeviceAuthorizedViewSet):

    ordering = ("date_created",)


class GCMDeviceViewSet(GCMDeviceAuthorizedViewSet):

    ordering = ("date_created",)


class AnnouncementViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    serializer_class = AnnouncementDetailSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Announcement.objects.filter(
                created_by=self.request.user
            ).prefetch_related("users", "groups", "events", "meetings")
        return Announcement.objects.none()

    def get_serializer_class(self):
        if self.action in ["list"]:
            return AnnouncementListSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            AnnouncementListSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    @decorators.action(detail=True, methods=["POST"])
    def send(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.sent:
            raise exceptions.ValidationError("message already sent")

        instance.send()

        track(
            request.user,
            "announcement.send",
            properties={"announcement_id": instance.id},
        )

        return Response(
            {"status": "message queued for sending"}, status=status.HTTP_202_ACCEPTED
        )
