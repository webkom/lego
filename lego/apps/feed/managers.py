from stream_framework.feed_managers.base import (FanoutPriority, Manager, add_operation,
                                                 remove_operation)
from stream_framework.utils import get_metrics_instance

from .feeds import NotificationFeed


class NotificationFeedManager:
    """
    This manager is used to manage actions in the notification feed. This manager supports adding
    and removing an activity from one or more feeds based on a list of user ids. Each user has
    his own feed based on the user id.
    """

    feed_classes = dict(
        notifications=NotificationFeed
    )

    metrics = get_metrics_instance()

    create_fanout_tasks = Manager.create_fanout_tasks
    get_fanout_task = Manager.get_fanout_task
    priority_fanout_task = Manager.priority_fanout_task
    fanout_chunk_size = Manager.fanout_chunk_size
    fanout = Manager.fanout

    def get_feed(self, feed_key):
        return NotificationFeed(feed_key)

    def get_user_feed(self, user_id):
        return self.get_feed(user_id)

    def add_activity(self, user_ids, activity):
        operation_kwargs = dict(activities=[activity], trim=True)

        for feed_class in self.feed_classes.values():
            self.create_fanout_tasks(
                user_ids,
                feed_class,
                add_operation,
                operation_kwargs=operation_kwargs,
                fanout_priority=FanoutPriority.HIGH
            )
        self.metrics.on_activity_published()

    def remove_activity(self, user_ids, activity):
        operation_kwargs = dict(activities=[activity], trim=False)

        for feed_class in self.feed_classes.values():
            self.create_fanout_tasks(
                user_ids,
                feed_class,
                remove_operation,
                operation_kwargs=operation_kwargs,
                fanout_priority=FanoutPriority.HIGH
            )
        self.metrics.on_activity_removed()


notification_feed_manager = NotificationFeedManager()
