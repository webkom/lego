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
        instance_update.delay(instance)

    def on_delete(self, instance):
        instance_removal.delay(instance)
