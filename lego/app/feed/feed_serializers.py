from django.utils.six import BytesIO
from django.utils.timezone import is_aware, make_naive
from pytz import utc
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from stream_framework.serializers.base import BaseAggregatedSerializer, BaseSerializer
from stream_framework.verbs import get_verb_by_id

from lego.app.feed.activities import FeedActivity

from .serializers import StoreActivitySerializer, StoreAggregatedActivitySerializer


class FeedActivitySerializer(BaseSerializer):
    """
    This serializer is used to serialize and deserialize our custom activity.
    """

    def check_type(self, data):
        if not isinstance(data, FeedActivity):
            raise ValueError('We only know how to dump FeedActivities, not %s' % type(data))

    def dumps(self, activity):
        self.check_type(activity)
        # keep the milliseconds
        serializer = StoreActivitySerializer(instance=activity)
        return JSONRenderer().render(serializer.data)

    def loads(self, serialized_activity):
        stream = BytesIO(serialized_activity.encode('utf-8'))
        data = JSONParser().parse(stream)
        serializer = StoreActivitySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return self.dict_to_object(serializer.validated_data)

    def dict_to_object(self, payload):
        verb = get_verb_by_id(payload['verb']['id'])
        extra_context = payload['extra_context']
        activity_datetime = payload['time']

        activity = self.activity_class(
            payload['actor'], verb, payload['object'], payload['target'],
            time=activity_datetime, extra_context=extra_context
        )

        return activity


class AggregatedFeedSerializer(BaseAggregatedSerializer):
    """
    This serializer is used to serialize and deserialize the aggregated feed with our custom
    activity.
    """
    dehydrate = False
    date_fields = ['created_at', 'updated_at', 'seen_at', 'read_at']

    activity_serializer_class = FeedActivitySerializer(FeedActivity)

    def dumps(self, aggregated):
        self.check_type(aggregated)
        serializer = StoreAggregatedActivitySerializer(instance=aggregated)
        return JSONRenderer().render(serializer.data)

    def loads(self, serialized_aggregated):
        stream = BytesIO(serialized_aggregated.encode('utf-8'))
        data = JSONParser().parse(stream)
        serializer = StoreAggregatedActivitySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return self.dict_to_object(serializer.validated_data)

    def dict_to_object(self, payload):
        group = payload['group']
        aggregated = self.aggregated_activity_class(group)

        for date_field in self.date_fields:
            time = payload[date_field]
            if time and is_aware(time):
                time = make_naive(time, timezone=utc)
            setattr(aggregated, date_field, time)

        # write the activities
        if self.dehydrate:
            activity_ids = list(map(int, payload['dehydrated_ids']))
            aggregated._activity_ids = activity_ids
            aggregated.dehydrated = True
        else:
            aggregated.activities = list(map(self.activity_serializer_class.dict_to_object,
                                             payload['activities']))
            aggregated.dehydrated = False

        # write the minimized activities
        aggregated.minimized_activities = payload['minimized_activities']

        return aggregated
