from lego import celery_app
from lego.apps.feed.registry import get_handler


@celery_app.task(serializer='pickle')
def add_to_feeds(instance, action='update'):
    """
    Add action to feed and notificationfeed of appropriate users
    """

    handler = get_handler(instance._meta.model)
    if handler is None:
        # No handler registered for model
        return

    handler.handle_event(instance, action)
