from lego import celery_app
from lego.utils.content_types import split_string, string_to_instance, string_to_model_cls

from .registry import get_model_index


@celery_app.task(serializer='json')
def instance_update(instance_string):
    """
    Update a instance in the index. This function always retrieves the instance from the
    database, this makes sure delayed tasks injects the newest update into the index.
    """
    instance = string_to_instance(instance_string)
    model_index = get_model_index(instance._meta.model)
    if model_index:
        instance.refresh_from_db()
        model_index.update_instance(instance)


@celery_app.task(serializer='json')
def instance_removal(instance_string):
    """
    Remove a instance from the index. This is done by knowing the type and id of the object.
    """
    content_type_string, id_string = split_string(instance_string)
    model_cls = string_to_model_cls(content_type_string)

    model_index = get_model_index(model_cls)
    if model_index:
        model_index.remove_instance(id_string)
