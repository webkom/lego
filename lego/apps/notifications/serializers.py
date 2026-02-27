from rest_framework import serializers

from expo_notifications.models import Device

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.meetings.serializers import MeetingListSerializer
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer

from .models import Announcement, NotificationSetting


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = ("notification_type", "enabled", "channels")
        read_only_fields = ("notification_type",)


class NotificationSettingCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    class Meta:
        model = NotificationSetting
        fields = ("notification_type", "enabled", "channels")


class AnnouncementListSerializer(BasisModelSerializer):
    users = PublicUserSerializer(many=True, read_only=True)
    groups = PublicAbakusGroupSerializer(many=True, read_only=True)
    events = EventReadSerializer(many=True, read_only=True)
    meetings = MeetingListSerializer(many=True, read_only=True)
    from_group = PublicAbakusGroupSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = (
            "id",
            "message",
            "from_group",
            "sent",
            "users",
            "groups",
            "events",
            "exclude_waiting_list",
            "meetings",
            "meeting_invitation_status",
        )
        read_only_fields = ("sent",)


class AnnouncementDetailSerializer(BasisModelSerializer):
    class Meta(AnnouncementListSerializer.Meta):
        model = Announcement
        fields = (
            "id",
            "message",
            "from_group",
            "sent",
            "users",
            "groups",
            "events",
            "exclude_waiting_list",
            "meetings",
            "meeting_invitation_status",
        )
        read_only_fields = ("sent",)


class ExpoDeviceSerializer(BasisModelSerializer):
    class Meta:
        model = Device
        fields = ("push_token",)

    def validate_push_token(self, token: str) -> str:
        token = token.strip()

        if not token.startswith("ExponentPushToken[") or not token.endswith("]"):
            raise serializers.ValidationError("Invalid Expo Push Token")

        return token
