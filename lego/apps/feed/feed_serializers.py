from django.utils.six import BytesIO
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from stream_framework.serializers.base import BaseAggregatedSerializer
from stream_framework.utils.five import long_t
from stream_framework.verbs import get_verb_by_id


class StoreActivitySerializer(serializers.Serializer):
    """
    This serializer is used to serialize our custom activity. The DRF serializer is a convenient
    way to do this. Used for storage inside a aggregated activity.
    """
    time = serializers.DateTimeField()
    verb = serializers.IntegerField(source='verb.id')
    actor = serializers.CharField()
    object = serializers.CharField(allow_null=True)
    target = serializers.CharField(allow_null=True)
    extra_context = serializers.DictField(default={}, required=False)


class AggregatedActivitySerializer(BaseAggregatedSerializer):
    """
    This serializer is used to serialize and deserialize the aggregated feed with our custom
    activity.
    """
    dehydrate = False

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    def dumps(self, aggregated):
        self.check_type(aggregated)
        activities_serializer = StoreActivitySerializer(many=True, instance=aggregated.activities)
        return self.model(
            activity_id=long_t(aggregated.serialization_id),
            activities=JSONRenderer().render(activities_serializer.data),
            group=aggregated.group,
            created_at=aggregated.created_at,
            updated_at=aggregated.updated_at,
            seen_at=aggregated.seen_at,
            read_at=aggregated.read_at,
            minimized_activities=aggregated.minimized_activities,
        )

    def loads(self, serialized_aggregated):
        aggregated = self.aggregated_activity_class(
            group=serialized_aggregated['group'],
            activities=self.parse_serialized_activities(serialized_aggregated['activities']),
            created_at=serialized_aggregated['created_at'],
            updated_at=serialized_aggregated['updated_at'],
            read_at=serialized_aggregated['read_at'],
            seen_at=serialized_aggregated['seen_at']
        )
        aggregated.minimized_activities = serialized_aggregated['minimized_activities'] or 0
        return aggregated

    def parse_serialized_activities(self, serialized_activities):
        """
        Parse the activities bytes using the serializer.
        """
        data = JSONParser().parse(BytesIO(serialized_activities))
        serializer = StoreActivitySerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return self.activities_list_to_objects(serializer.validated_data)

    def activities_list_to_objects(self, activities_list):
        """
        Create activities based on the serializer data.
        """
        def create_object(activity):
            verb = get_verb_by_id(activity['verb']['id'])
            extra_context = activity['extra_context']
            activity_datetime = activity['time']

            activity = self.activity_class(
                activity['actor'], verb, activity['object'], activity['target'],
                time=activity_datetime, extra_context=extra_context
            )

            return activity

        return list(map(create_object, activities_list))
