from __future__ import annotations

from typing import List, Union

from django.db import IntegrityError, models
from django.db.models.query import QuerySet

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.marker import MarkerModelMixin


class FeedBase(models.Model):
    """
    FeedBase contains all the base components of a feed
    """

    ordering_key = models.CharField(max_length=48, db_index=True, default="0")
    feed_id = models.CharField(max_length=64, db_index=True)
    group = models.CharField(max_length=128)

    activity_store = models.JSONField(default=list)
    minimized_activities = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    max_aggregated_activities_length = 10

    class Meta:
        abstract = True

    @property
    def actor_ids(self):
        return [activity.actor_id for activity in self.activities]

    @property
    def verb(self):
        last_activity = self.last_activity
        if last_activity:
            return last_activity.verb.infinitive
        return "unknown"

    @property
    def activities(self):
        return [Activity.deserialize(activity) for activity in self.activity_store]

    @property
    def last_activity(self):
        if self.activity_store:
            return self.activities[0]

    @property
    def activity_count(self):
        return self.minimized_activities + len(self.activity_store)

    @classmethod
    def create_activities(cls, activity, feed_ids, group):
        def create_activity(activity, feed_id, group):
            aggregated_activity = cls(feed_id=feed_id, group=group)
            aggregated_activity.add_activity(activity)
            return aggregated_activity

        result = cls.objects.bulk_create(
            [create_activity(activity, feed_id, group) for feed_id in feed_ids]
        )

        return [activity.id for activity in result]

    def add_activity(self, activity):
        """
        Add activity to the activity store
        """
        if not self.activity_store:
            activities = []
        else:
            activities = list(self.activity_store)

        activities.insert(0, activity.serialize())
        self.activity_store = activities
        self.ordering_key = activity.activity_id

    def remove_activity(self, activity):
        """
        Remove activity from self, delete self if no other activities is present in the
        activity_store.
        """
        if isinstance(self.activity_store, list):
            for raw_activity in self.activity_store:
                if raw_activity.get("activity_id") == str(activity.activity_id):
                    self.activity_store.remove(raw_activity)
        if self.last_activity:
            self.ordering_key = self.last_activity.activity_id
        else:
            self.ordering_key = "0"


class AggregatedFeedManager(models.Manager):
    def find_matching_groups(
        self, group, offset, feed_ids
    ) -> Union[QuerySet, List[AggregatedFeedBase]]:
        """
        TODO: Implement offset filtering?
        """
        q = self.get_queryset()
        return q.filter(group=group, feed_id__in=feed_ids)


class AggregatedFeedBase(FeedBase):
    objects = AggregatedFeedManager()

    class Meta(FeedBase.Meta):
        abstract = True
        ordering = ("-ordering_key",)


class NotificationFeedBase(FeedBase, MarkerModelMixin):
    objects = AggregatedFeedManager()

    class Meta(FeedBase.Meta):
        abstract = True
        ordering = ("-ordering_key",)

    def add_activity(self, activity):
        super().add_activity(activity)
        self.mark_insert_activity(self.feed_id, activity.activity_id)

    def remove_activity(self, activity):
        super().remove_activity(activity)
        self.mark_activity(self.feed_id, activity.activity_id, True, True)


class TimelineStorage(models.Model):
    """
    Timeline storage stores the location of activities inside the aggregated feeds.
    """

    activity_id = models.CharField(max_length=48, db_index=True)
    feed = models.CharField(max_length=32, db_index=True)
    aggregated_id = models.PositiveIntegerField(db_index=True)

    class Meta:
        unique_together = ("activity_id", "feed")

    @classmethod
    def aggregated_ids(cls, activity_id, feed):
        return list(
            cls.objects.filter(
                activity_id=str(activity_id), feed=feed._meta.model_name
            ).values_list("aggregated_id", flat=True)
        )

    @classmethod
    def add_ids(cls, activity_id, aggregated_ids, feed):
        """
        Naive solution without bulk support.
        """
        for aggregated_id in aggregated_ids:
            try:
                cls.objects.update_or_create(
                    activity_id=str(activity_id),
                    feed=feed._meta.model_name,
                    aggregated_id=aggregated_id,
                )
            except IntegrityError:
                pass

    @classmethod
    def remove_ids(cls, activity_id, aggregated_ids, feed):
        return cls.objects.filter(
            activity_id=str(activity_id),
            feed=feed._meta.model_name,
            aggregated_id__in=aggregated_ids,
        ).delete()


"""
The models bellow this line implements the actual feeds.
"""


class PersonalFeed(AggregatedFeedBase):
    pass


class UserFeed(AggregatedFeedBase):
    pass


class NotificationFeed(NotificationFeedBase):
    pass
