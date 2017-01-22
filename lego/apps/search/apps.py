from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from . import backend
from .backends.elasticsearch import ElasticsearchBackend


class SearchConfig(AppConfig):
    name = 'lego.apps.search'
    verbose_name = 'Search'

    def ready(self):
        super().ready()
        """
        This magic executes modules named search_indexes in every installed app. Search indexes
        is registered this way.
        """

        # Simple way to initialize the search backend. We may change this in the future.
        search_backed = ElasticsearchBackend()
        search_backed.set_up()
        backend.current_backend = search_backed

        autodiscover_modules('search_indexes')
        from .signals import post_save_callback, post_delete_callback  # noqa
