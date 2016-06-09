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


class MarkSerializer(serializers.Serializer):
    seen = serializers.BooleanField(default=False)
    read = serializers.BooleanField(default=False)


class StoreActivitySerializer(serializers.Serializer):
    """
    This serializer is used to serialize our custom activity. The DRF serializer is a convenient
    way to do this. Used for storage.
    """
    time = serializers.DateTimeField()
    verb = serializers.IntegerField(source='verb.id')
    actor = serializers.CharField()
    object = serializers.CharField(allow_null=True)
    target = serializers.CharField(allow_null=True)
    extra_context = serializers.DictField(default={}, required=False)


class StoreAggregatedActivitySerializer(serializers.Serializer):
    """
    This serializer is used to serialize a aggregated feed with our custom activity class. The DRF
    serializer is a convenient way to do this. Used for storage.
    """
    group = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    seen_at = serializers.DateTimeField(allow_null=True)
    read_at = serializers.DateTimeField(allow_null=True)

    activities = StoreActivitySerializer(many=True)
    dehydrated_ids = serializers.ListField(source='_activity_ids')
    minimized_activities = serializers.IntegerField()
