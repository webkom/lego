from django.contrib.postgres.fields import JSONField
from django.db import models


class FeedBase(models.Model):
    """
    FeedBase contains all the base components of a feed
    """
    activity_id = models.CharField(max_length=20)
    feed_id = models.CharField(max_length=64)
    group = models.CharField(max_length=128)

    activities = JSONField()
    minimized_activities = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    max_aggregated_activities_length = 10

    class Meta:
        abstract = True

    @property
    def actor_ids(self):
        return []


class AggregatedFeedBase(FeedBase):
    class Meta(FeedBase.Meta):
        abstract = True


class NotificationFeedBase(FeedBase):
    class Meta(FeedBase.Meta):
        pass

    def seen_at(self, user):
        pass

    def read_at(self, user):
        pass


"""
The models bellow this line implements the actual feeds.
"""


class PersonalFeed(AggregatedFeedBase):
    pass


class UserFeed(AggregatedFeedBase):
    pass


class NotificationFeed(NotificationFeedBase):
    pass
