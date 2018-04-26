from django.core.exceptions import ObjectDoesNotExist

from lego import celery_app
from lego.utils.content_types import string_to_instance
from lego.utils.tasks import AbakusTask

from . import registry


@celery_app.task(bind=True, base=AbakusTask)
def execute_action_handler(self, instance, action, kwargs, logger_context=None):
    self.setup_logger(logger_context)

    try:
        instance = string_to_instance(instance)
    except ObjectDoesNotExist as e:
        # Retry, the object may not be present in DB
        raise self.retry(exc=e, max_retries=3, countdown=20)

    handler = registry.get_handler_by_instance(instance)
    return handler.run(instance, action, **kwargs)
