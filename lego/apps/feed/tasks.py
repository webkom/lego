from lego import celery_app
from lego.apps.feed.managers import notification_feed_manager
from lego.apps.feed.registry import get_handler


class InstanceEventTask(celery_app.Task):

    @classmethod
    def add_to_feeds(cls, instance, action):
        task = cls()
        task.delay(instance, action)

    def run(self, instance, action='update'):
        """
        Add action to feed and notificationfeed of appropriate users
        """

        Handler_cls = get_handler(instance._meta.model)
        handler = Handler_cls(instance, action)

        activity = handler.activity
        user_ids = handler.user_ids

        if len(user_ids) > 0:
            notification_feed_manager.add_activity(
                user_ids=user_ids,
                activity=activity
            )
