from oauth2_provider.models import clear_expired
from structlog import get_logger

from lego import celery_app
from lego.utils.tasks import AbakusTask

log = get_logger()


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def clear_expired_oauth_tokens(self, logger_context=None):
    """Prune expired tokens - every client_credentials grant mints a new one."""
    self.setup_logger(logger_context)
    clear_expired()
