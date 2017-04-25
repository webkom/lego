from rest_framework import serializers

from lego.apps.feed.fields import FeedDateTimeField


class FeedActivitySerializer(serializers.Serializer):
    time = FeedDateTimeField()
    extra_context = serializers.DictField(default={})
    actor = serializers.CharField()
    object = serializers.CharField()
    target = serializers.CharField()


class AggregatedFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='serialization_id')
    verb = serializers.CharField(source='verb.infinitive')
    created_at = FeedDateTimeField()
    updated_at = FeedDateTimeField()
    last_activity = FeedActivitySerializer()
    activities = FeedActivitySerializer(many=True)
    activity_count = serializers.IntegerField()
    actor_ids = serializers.ListField(child=serializers.IntegerField())


class MarkSerializer(serializers.Serializer):
    seen = serializers.BooleanField(default=False)
    read = serializers.BooleanField(default=False)


class NotificationFeedSerializer(AggregatedFeedSerializer):
    read = serializers.BooleanField(source='is_read')
    seen = serializers.BooleanField(source='is_seen')
