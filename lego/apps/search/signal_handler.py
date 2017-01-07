from lego.utils.content_types import instance_to_string

from .registry import get_model_index
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
        """
        Update the search index when we know how to index the instance.
        """
        identifier = instance_to_string(instance)
        search_index = get_model_index(instance)
        if identifier and search_index:
            instance_update.delay(identifier)

    def on_delete(self, instance):
        """
        Remove the instance from the index if the instance has a search_index
        """
        identifier = instance_to_string(instance)
        search_index = get_model_index(instance)
        if identifier and search_index:
            instance_removal.delay(identifier)
