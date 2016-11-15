from .tasks import add_to_feeds


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
        add_to_feeds(instance, action='create')

    def on_update(self, instance):
        add_to_feeds(instance, action='update')

    def on_delete(self, instance):
        add_to_feeds(instance, action='delete')
