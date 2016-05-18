import pickle

import six
from stream_framework.exceptions import SerializationException
from stream_framework.serializers.base import BaseAggregatedSerializer, BaseSerializer
from stream_framework.serializers.utils import check_reserved
from stream_framework.utils import datetime_to_epoch, epoch_to_datetime
from stream_framework.verbs import get_verb_by_id

from lego.app.feed.activities import FeedActivity


"""
Because of our custom FeedActivity we need custom serializers. They looks ugly but all they do is
to transform a activity to a format that can be stored in Redis.
"""


class FeedActivitySerializer(BaseSerializer):

    def check_type(self, data):
        if not isinstance(data, FeedActivity):
            raise ValueError('we only know how to dump activities, not %s' % type(data))

    def dumps(self, activity):
        self.check_type(activity)
        # keep the milliseconds
        activity_time = '%.6f' % datetime_to_epoch(activity.time)
        parts = [
            activity.verb.id, activity.actor_id, activity.object_id, activity.target_id,
            activity.actor_content_type, activity.object_content_type,
            activity.target_content_type
        ]
        extra_context = activity.extra_context.copy()
        pickle_string = ''
        if extra_context:
            pickle_string = pickle.dumps(activity.extra_context)
            if six.PY3:
                pickle_string = pickle_string.decode('latin1')
        parts += [activity_time, pickle_string]
        serialize_parts = map(lambda x: x if x is not None else 0, parts)
        serialized_activity = ','.join(map(str, serialize_parts))
        return serialized_activity

    def loads(self, serialized_activity):
        parts = serialized_activity.split(',', 9)
        # convert these to ids
        verb_id, actor_id, object_id, target_id = map(int, parts[:4])
        actor_content_type, object_content_type, target_content_type = map(str, parts[4:7])

        def combine_identifier(object_id, object_content_type):
            if object_id and object_content_type:
                return '{0}-{1}'.format(object_content_type, object_id)
            return None

        actor = combine_identifier(actor_id, actor_content_type)
        object_ = combine_identifier(object_id, object_content_type)
        target = combine_identifier(target_id, target_content_type)

        activity_datetime = epoch_to_datetime(float(parts[7]))
        pickle_string = parts[8]
        verb = get_verb_by_id(verb_id)
        extra_context = {}
        if pickle_string:
            if six.PY3:
                pickle_string = pickle_string.encode('latin1')
            extra_context = pickle.loads(pickle_string)
        activity = self.activity_class(
            actor, verb, object_, target,
            time=activity_datetime, extra_context=extra_context
        )

        return activity


class AggregatedFeedSerializer(BaseAggregatedSerializer):
    dehydrate = False
    identifier = 'v3'
    reserved_characters = [';', ',', ';;']
    date_fields = ['created_at', 'updated_at', 'seen_at', 'read_at']

    activity_serializer_class = FeedActivitySerializer

    def dumps(self, aggregated):
        self.check_type(aggregated)

        activity_serializer = self.activity_serializer_class(FeedActivity)
        # start by storing the group
        parts = [aggregated.group]
        check_reserved(aggregated.group, [';;'])

        # store the dates
        for date_field in self.date_fields:
            value = getattr(aggregated, date_field)
            if value is not None:
                # keep the milliseconds
                epoch = '%.6f' % datetime_to_epoch(value)
            else:
                epoch = -1
            parts += [epoch]

        # add the activities serialization
        serialized_activities = []
        if self.dehydrate:
            if not aggregated.dehydrated:
                aggregated = aggregated.get_dehydrated()
            serialized_activities = map(str, aggregated._activity_ids)
        else:
            for activity in aggregated.activities:
                serialized = activity_serializer.dumps(activity)
                check_reserved(serialized, [';', ';;'])
                serialized_activities.append(serialized)

        serialized_activities_part = ';'.join(serialized_activities)
        parts.append(serialized_activities_part)

        # add the minified activities
        parts.append(aggregated.minimized_activities)

        # stick everything together
        serialized_aggregated = ';;'.join(map(str, parts))
        serialized = '%s%s' % (self.identifier, serialized_aggregated)
        return serialized

    def loads(self, serialized_aggregated):
        activity_serializer = self.activity_serializer_class(FeedActivity)
        try:
            serialized_aggregated = serialized_aggregated[2:]
            parts = serialized_aggregated.split(';;')
            # start with the group
            group = parts[0]
            aggregated = self.aggregated_activity_class(group)

            # get the date and activities
            date_dict = dict(zip(self.date_fields, parts[1:5]))
            for k, v in date_dict.items():
                date_value = None
                if v != '-1':
                    date_value = epoch_to_datetime(float(v))
                setattr(aggregated, k, date_value)

            # write the activities
            serializations = parts[5].split(';')
            if self.dehydrate:
                activity_ids = list(map(int, serializations))
                aggregated._activity_ids = activity_ids
                aggregated.dehydrated = True
            else:
                activities = [activity_serializer.loads(s)
                              for s in serializations]
                aggregated.activities = activities
                aggregated.dehydrated = False

            # write the minimized activities
            minimized = int(parts[6])
            aggregated.minimized_activities = minimized

            return aggregated
        except Exception as e:
            msg = six.text_type(e)
            raise SerializationException(msg)
