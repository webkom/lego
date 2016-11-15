from lego import celery_app

from .registry import get_model_index


@celery_app.task(serializer='pickle')
def instance_update(instance):
    """
    Update a instance in the index. This function always retrieves the instance from the
    database, this makes sure delayed tasks injects the newest update into the index.

    TODO: Change to json task serializer.
    """
    model_index = get_model_index(instance._meta.model)
    if model_index:
        instance.refresh_from_db()
        model_index.update_instance(instance)


@celery_app.task(serializer='pickle')
def instance_removal(instance):
    """
    Remove a instance from the index. This is done by knowing the type and id of the object.

    TODO: Change to json task serializer.
    """
    model_index = get_model_index(instance._meta.model)
    if model_index:
        model_index.remove_instance(instance)
