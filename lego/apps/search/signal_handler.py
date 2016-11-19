from lego.utils.content_types import instance_to_string

from .tasks import instance_removal, instance_update


class BaseSignalHandler:

    def on_save(self, instance):
        pass

    def on_delete(self, instance):
        pass


class AsyncSignalHandler(BaseSignalHandler):
    """
    This handler indexes model changes using async celery tasks.
    """

    def on_save(self, instance):
        identifier = instance_to_string(instance)
        instance_update.delay(identifier)

    def on_delete(self, instance):
        identifier = instance_to_string(instance)
        instance_removal.delay(identifier)
