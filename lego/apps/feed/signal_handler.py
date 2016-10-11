from .tasks import InstanceCreateTask, InstanceRemovalTask, InstanceUpdateTask


class BaseSignalHandler:
    def on_create(self, instance):
        pass

    def on_update(self, instance):
        pass

    def on_delete(self, instance):
        pass


class AsyncSignalHandler(BaseSignalHandler):
    """
    This handler indexes model changes using async celery tasks.
    """

    def on_create(self, instance):
        InstanceCreateTask.create_instance(instance)

    def on_update(self, instance):
        InstanceUpdateTask.update_instance(instance)

    def on_delete(self, instance):
        InstanceRemovalTask.remove_instance(instance)
