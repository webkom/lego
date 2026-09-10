from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from lego.apps.feeds.context import resolve_context


class FeedActivitySerializer(serializers.Serializer):
    activity_id = serializers.CharField(read_only=True)
    verb = serializers.IntegerField(source="verb.id")
    time = serializers.DateTimeField()
    extra_context = serializers.DictField(default={})
    actor = serializers.CharField(required=False, allow_null=True)
    object = serializers.CharField()
    target = serializers.CharField(required=False, allow_null=True)


class AggregatedFeedSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ordering_key = serializers.CharField()
    verb = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    last_activity = FeedActivitySerializer()
    activities = FeedActivitySerializer(many=True)
    activity_count = serializers.IntegerField()
    actor_ids = serializers.ListField(child=serializers.CharField())
    context = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DictField())
    def get_context(self, obj):
        return resolve_context(obj, self.context.get("attr_lookup", {}))


class MarkSerializer(serializers.Serializer):
    seen = serializers.BooleanField(default=False)
    read = serializers.BooleanField(default=False)


class AggregatedMarkedFeedSerializer(AggregatedFeedSerializer):
    read = serializers.BooleanField(source="is_read")
    seen = serializers.BooleanField(source="is_seen")
