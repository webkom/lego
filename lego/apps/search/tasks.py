from lego import celery_app

from .registry import get_model_index


class InstanceUpdateTask(celery_app.Task):

    @classmethod
    def update_instance(cls, instance):
        task = cls()
        task.delay(instance)

    def run(self, instance):
        """
        Update a instance in the index. This function always retrieves the instance from the
        database, this makes sure delayed tasks injects the newest update into the index.
        """
        model_index = get_model_index(instance._meta.model)
        if model_index:
            instance.refresh_from_db()
            model_index.update_instance(instance)


class InstanceRemovalTask(celery_app.Task):

    @classmethod
    def remove_instance(cls, instance):
        task = cls()
        task.delay(instance)

    def run(self, instance):
        """
        Remove a instance from the index. This is done by knowing the type and id of the object.
        """
        model_index = get_model_index(instance._meta.model)
        if model_index:
            model_index.remove_instance(instance)
