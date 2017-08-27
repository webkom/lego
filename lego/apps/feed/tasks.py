from structlog import get_logger

from lego import celery_app
from lego.apps.feed.registry import get_handler
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer='pickle', bind=True, base=AbakusTask)
def add_to_feeds(self, instance, action='update', logger_context=None):
    """
    Add action to feed and notificationfeed of appropriate users
    """
    self.setup_logger(logger_context)

    handler = get_handler(instance._meta.model)
    if handler is None:
        # No handler registered for model
        return

    handler.handle_event(instance, action)
