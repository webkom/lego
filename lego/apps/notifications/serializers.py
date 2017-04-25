from rest_framework import serializers

from .models import NotificationSetting


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
