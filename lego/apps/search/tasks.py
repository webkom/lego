from structlog import get_logger

from lego import celery_app
from lego.utils.content_types import string_to_instance

from .registry import get_content_type_index, get_model_index

log = get_logger()


@celery_app.task(serializer='json')
def instance_delete(identifier):
    content_type, pk = identifier.split('-')
    index = get_content_type_index(content_type)
    if index:
        index.remove_instance(pk)


@celery_app.task(serializer='json')
def instance_update(identifier):
    """
    Update a instance in the index. This function always retrieves the instance from the
    database, this makes sure delayed tasks injects the newest update into the index.
    """
    instance = string_to_instance(identifier)
    if instance:
        index = get_model_index(instance)
        index.update_instance(instance)
    else:
        # Could not find the instance in the DB. Call the instance_delete task to make sure the
        # object gets removed from our index.
        log.warn('search_update_non_existing_instance', identifier=identifier)
        instance_delete.delay(identifier)
