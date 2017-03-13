from lego import celery_app

from .sync import Sync


@celery_app.task()
def sync_external_systems():
    """
    Sync external systems.
    """
    sync = Sync()
    sync.sync()
