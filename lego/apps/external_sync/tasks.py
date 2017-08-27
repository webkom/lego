from lego import celery_app
from lego.utils.tasks import AbakusTask

from .sync import Sync


@celery_app.task(bind=True, base=AbakusTask)
def sync_external_systems(self, logger_context=None):
    """
    Sync external systems.
    """
    self.setup_logger(logger_context)

    sync = Sync()
    sync.sync()
