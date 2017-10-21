from lego.apps.feed.registry import handler_exists

from .tasks import add_to_feeds


class BaseSignalHandler:
    def on_create(self, instance):
        pass

    def on_update(self, instance):
        pass

    def on_delete(self, instance):
        pass


class AsyncSignalHandler(BaseSignalHandler):
    """
    This handler indexes model changes using async celery tasks.
    """

    def on_create(self, instance):
        if handler_exists(instance):
            add_to_feeds.delay(instance, action='create')

    def on_update(self, instance):
        if handler_exists(instance):
            add_to_feeds.delay(instance, action='update')

    def on_delete(self, instance):
        if handler_exists(instance):
            add_to_feeds.delay(instance, action='delete')
