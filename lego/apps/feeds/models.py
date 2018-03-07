from django.contrib.postgres.fields import JSONField
from django.db import models

from lego.apps.feeds.marker import MarkerModelMixin

from .verbs import verbs


class FeedBase(models.Model):
    """
    FeedBase contains all the base components of a feed
    """
    feed_id = models.CharField(max_length=64, db_index=True)
    group = models.CharField(max_length=128)

    activity_store = JSONField()
    minimized_activities = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    max_aggregated_activities_length = 10

    class Meta:
        abstract = True

    @property
    def actor_ids(self):
        return []

    @property
    def verb(self):
        return verbs[2].infinitive

    @property
    def activities(self):
        return []

    @property
    def last_activity(self):
        return

    @property
    def activity_count(self):
        return 0


class AggregatedFeedBase(FeedBase):
    class Meta(FeedBase.Meta):
        abstract = True


class NotificationFeedBase(FeedBase, MarkerModelMixin):

    seen_at = models.DateTimeField(null=True)
    read_at = models.DateTimeField(null=True)

    class Meta(FeedBase.Meta):
        abstract = True


class TimelineStorage(models.Model):
    """
    Timeline storage stores the location of activities inside the aggregated feed.
    """

    activity_id = models.CharField(max_length=20, db_index=True)
    feed = models.CharField(max_length=32, db_index=True)
    aggregated_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('activity_id', 'feed')

    @classmethod
    def aggregated_ids(cls, activity_id, feed):
        return cls.objects.filter(activity_id=activity_id, feed=feed._meta.model_name).values_list(
            'aggregated_id', flat=True
        )


"""
The models bellow this line implements the actual feeds.
"""


class PersonalFeed(AggregatedFeedBase):
    pass


class UserFeed(AggregatedFeedBase):
    pass


class NotificationFeed(NotificationFeedBase):
    pass
