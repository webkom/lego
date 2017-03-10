import logging

from stream_framework.feed_managers.base import FanoutPriority, add_operation, remove_operation
from stream_framework.tasks import (fanout_operation, fanout_operation_hi_priority,
                                    fanout_operation_low_priority)
from stream_framework.utils import chunks, get_metrics_instance
from structlog import get_logger

from lego.apps.feed import tasks
from lego.apps.feed.feed import NotificationFeed

logger = logging.getLogger(__name__)
log = get_logger()


class FeedManager:
    """
    A feed manager is responsible for adding activities to a set of feeds. This class contains some
    helper functions that makes async fanout easier.
    """

    priority_fanout_task = {
        FanoutPriority.HIGH: fanout_operation_hi_priority,
        FanoutPriority.LOW: fanout_operation_low_priority
    }

    fanout_chunk_size = 100

    metrics = get_metrics_instance()

    def add_activity(self, activity, recipients, feed_classes):
        """
        Simple fanout a task to a set of recipients.
        """
        if NotificationFeed in feed_classes and activity:
            mailer_task = getattr(tasks, f'mail_{activity.verb.infinitive}', lambda: "not found")
            if not mailer_task == "not found":
                mailer_task.delay(activity, recipients)

        operation_kwargs = dict(activities=[activity], trim=True)

        for feed_class in feed_classes:
            self.create_fanout_tasks(
                set(recipients),
                feed_class,
                add_operation,
                operation_kwargs=operation_kwargs,
                fanout_priority=FanoutPriority.HIGH
            )
        self.metrics.on_activity_published()

    def remove_activity(self, activity, recipients, feed_classes):
        """
        Remove an activity from a set of recipient feeds.
        """
        operation_kwargs = dict(activities=[activity], trim=False)

        for feed_class in feed_classes:
            self.create_fanout_tasks(
                set(recipients),
                feed_class,
                remove_operation,
                operation_kwargs=operation_kwargs,
                fanout_priority=FanoutPriority.HIGH
            )
        self.metrics.on_activity_removed()

    def get_fanout_task(self, priority=None, feed_class=None):
        """
        Returns the fanout task taking priority in account.
        """

        return self.priority_fanout_task.get(priority, fanout_operation)

    def create_fanout_tasks(self, follower_ids, feed_class, operation,
                            operation_kwargs=None, fanout_priority=None):
        """
        Creates the fanout task for the given activities and feed classes
        followers
        It takes the following ids and distributes them per fanout_chunk_size
        into smaller tasks
        """

        fanout_task = self.get_fanout_task(fanout_priority, feed_class=feed_class)

        if not fanout_task:
            return []

        chunk_size = self.fanout_chunk_size
        user_ids_chunks = list(chunks(follower_ids, chunk_size))

        log.info('feed_spawn_tasks', subtasks=len(user_ids_chunks), recipients=len(follower_ids))

        tasks = []

        for ids_chunk in user_ids_chunks:
            task = fanout_task.delay(
                feed_manager=self,
                feed_class=feed_class,
                user_ids=ids_chunk,
                operation=operation,
                operation_kwargs=operation_kwargs
            )
            tasks.append(task)
        return tasks

    def fanout(self, user_ids, feed_class, operation, operation_kwargs):
        """
        This functionality is called from within stream_framework.tasks.fanout_operation
        This function is almost always called in async tasks created by stream_framework.
        """
        with self.metrics.fanout_timer(feed_class):
            batch_context_manager = feed_class.get_timeline_batch_interface()
            with batch_context_manager as batch_interface:
                log.info('feed_batch_fanout', recipients=len(user_ids))

                operation_kwargs['batch_interface'] = batch_interface
                for user_id in user_ids:
                    feed = feed_class(user_id)
                    operation(feed, **operation_kwargs)

        fanout_count = len(operation_kwargs['activities']) * len(user_ids)
        self.metrics.on_fanout(feed_class, operation, fanout_count)


feed_manager = FeedManager()
