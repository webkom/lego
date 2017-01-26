from rest_framework import serializers


class FeedActivitySerializer(serializers.Serializer):
    time = serializers.DateTimeField()
    extra_context = serializers.DictField(default={})
    actor = serializers.CharField()
    object = serializers.CharField()
    target = serializers.CharField()


class AggregatedFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='serialization_id')
    verb = serializers.CharField(source='verb.infinitive')
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    last_activity = FeedActivitySerializer()
    activity_count = serializers.IntegerField()
    actor_ids = serializers.ListField(child=serializers.IntegerField())


class MarkSerializer(serializers.Serializer):
    seen = serializers.BooleanField(default=False)
    read = serializers.BooleanField(default=False)
