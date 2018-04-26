from lego import celery_app
from lego.utils.tasks import AbakusTask

from .utils import fanout


@celery_app.task(bind=True, base=AbakusTask)
def feed_fanout(self, operation, activity, recipients, feed, logger_context=None):
    self.setup_logger(logger_context)
    return fanout(operation, activity, recipients, feed)
