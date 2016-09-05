from .tasks import InstanceRemovalTask, InstanceUpdateTask


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
        InstanceUpdateTask.update_instance(instance)

    def on_delete(self, instance):
        InstanceRemovalTask.remove_instance(instance)
