from rest_framework import serializers

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

    class Meta:
        model = Announcement
        fields = ('id', 'message', 'sent')
        read_only_fields = ('sent', )


class AnnouncementDetailSerializer(BasisModelSerializer):

    class Meta(AnnouncementListSerializer.Meta):
        model = Announcement
        fields = (
            'id', 'message', 'sent', 'users', 'groups', 'events', 'meetings',
        )
        read_only_fields = ('sent',)
