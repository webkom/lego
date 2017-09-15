from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.meetings.serializers import MeetingSerializer
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer

from .models import Announcement, NotificationSetting


class NotificationSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationSetting
        fields = ('notification_type', 'enabled', 'channels')
        read_only_fields = ('notification_type', )


class NotificationSettingCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = NotificationSetting
        fields = ('notification_type', 'enabled', 'channels')


class AnnouncementListSerializer(BasisModelSerializer):

    users = PublicUserSerializer(many=True, read_only=True)
    groups = PublicAbakusGroupSerializer(many=True, read_only=True)
    events = EventReadSerializer(many=True, read_only=True)
    meetings = MeetingSerializer(many=True, read_only=True)

    class Meta:
        model = Announcement
        fields = ('id', 'message', 'sent', 'users', 'groups', 'events', 'meetings',)
        read_only_fields = ('sent', )


class AnnouncementDetailSerializer(BasisModelSerializer):

    class Meta(AnnouncementListSerializer.Meta):
        model = Announcement
        fields = (
            'id', 'message', 'sent', 'users', 'groups', 'events', 'meetings',
        )
        read_only_fields = ('sent',)
