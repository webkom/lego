from django.utils.timezone import is_aware, make_naive
from pytz import utc
from stream_framework.activity import Activity, AggregatedActivity


class FeedActivity(Activity):
    """
    Custom activity class
    Stores actor, object and target as a content_identifier string.

    Actor - The user or object that performs an action.
    Object - The object the feed activity represents, this could be a comment.
    Target - The object the activity relates to, this is typically the object that was commented on.
    """
    def __init__(self, actor, verb, object, target=None, time=None, extra_context=None):
        # Make time native if it is timezone aware.
        if time and is_aware(time):
            time = make_naive(time, timezone=utc)
        super().__init__(actor, verb, object, target, time, extra_context)

    def _set_object_or_id(self, field, object_):
        id_field = '%s_id' % field
        content_type_field = '%s_content_type' % field

        if isinstance(object_, int):
            setattr(self, id_field, object_)
            setattr(self, content_type_field, None)
        elif isinstance(object_, str):
            content_type, object_id = object_.split('-')
            setattr(self, id_field, int(object_id))
            setattr(self, content_type_field, content_type)
        elif object_ is None:
            setattr(self, id_field, None)
            setattr(self, content_type_field, None)
        else:
            setattr(self, id_field, int(object_.id))
            setattr(self, content_type_field, '{0}.{1}'.format(
                object_._meta.app_label,
                object_._meta.model_name
            ))

    @property
    def actor(self):
        if self.actor_content_type and self.actor_id:
            return '{0}-{1}'.format(self.actor_content_type, self.actor_id)

    @property
    def object(self):
        if self.object_content_type and self.object_id:
            return '{0}-{1}'.format(self.object_content_type, self.object_id)

    @property
    def target(self):
        if self.target_content_type and self.target_id:
            return '{0}-{1}'.format(self.target_content_type, self.target_id)


class FeedAggregatedActivity(AggregatedActivity):
    max_aggregated_activities_length = 1
