from rest_framework import serializers


class FeedActivitySerializer(serializers.Serializer):
    time = serializers.DateTimeField()
    extra_context = serializers.DictField(default={})
    actor = serializers.CharField()
    object = serializers.CharField()
    target = serializers.CharField()


class AggregatedFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='activity_id')
    verb = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    last_activity = FeedActivitySerializer()
    activities = FeedActivitySerializer(many=True)
    activity_count = serializers.IntegerField()
    actor_ids = serializers.ListField(child=serializers.CharField())


class MarkSerializer(serializers.Serializer):
    seen = serializers.BooleanField(default=False)
    read = serializers.BooleanField(default=False)


class FeedMarkerMixinSerializer:
    read = serializers.BooleanField(source='is_read')
    seen = serializers.BooleanField(source='is_seen')


class AggregatedMarkedFeedSerializer(AggregatedFeedSerializer, FeedMarkerMixinSerializer):
    pass
