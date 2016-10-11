from lego import celery_app
from lego.apps.feed.managers import notification_feed_manager
from lego.apps.feed.registry import get_handler


class InstanceCreateTask(celery_app.Task):

    @classmethod
    def create_instance(cls, instance):
        task = cls()
        task.delay(instance)

    def run(self, instance):
        """
        Add action to feed and notificationfeed of appropriate users
        """

        Handler = get_handler(instance._meta.model)
        activity = Handler.get_activity(instance, action='create')
        user_ids = Handler.get_user_ids(instance, action='create')
        if len(user_ids) > 0:
            notification_feed_manager.add_activity(
                user_ids=user_ids,
                activity=activity
            )


class InstanceUpdateTask(celery_app.Task):

    @classmethod
    def update_instance(cls, instance):
        task = cls()
        task.delay(instance)

    def run(self, instance):
        """
        Add action to feed and notificationfeed of appropriate users
        """
        Handler = get_handler(instance._meta.model)
        activity = Handler.get_activity(instance, action='update')
        user_ids = Handler.get_user_ids(instance, action='update')
        if len(user_ids) > 0:
            notification_feed_manager.add_activity(
                user_ids=user_ids,
                activity=activity
            )


class InstanceRemovalTask(celery_app.Task):

    @classmethod
    def remove_instance(cls, instance):
        task = cls()
        task.delay(instance)

    def run(self, instance):
        """
        Add action to feed and notificationfeed of appropriate users
        """
        Handler = get_handler(instance._meta.model)
        activity = Handler.get_activity(instance, action='delete')
        user_ids = Handler.get_user_ids(instance, action='delete')
        if len(user_ids) > 0:
            notification_feed_manager.add_activity(
                user_ids=user_ids,
                activity=activity
            )
