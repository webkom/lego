from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import autodiscover_modules

from . import backend
from .backends.elasticsearch import ElasticsearchBackend
from .backends.postgres import PostgresBackend


class SearchConfig(AppConfig):
    name = "lego.apps.search"
    verbose_name = "Search"

    def ready(self):
        super().ready()
        """
        This magic executes modules named search_indexes in every installed app. Search indexes
        is registered this way.
        """
        # Simple way to initialize the search backend. We may change this in the future.
        if settings.SEARCH_BACKEND == "elasticsearch":
            search_backed = ElasticsearchBackend()
        elif settings.SEARCH_BACKEND == "postgres":
            search_backed = PostgresBackend()
        else:
            raise ValueError("Invalid search backend")

        search_backed.set_up()
        backend.current_backend = search_backed

        autodiscover_modules("search_indexes")
        from .signals import post_delete_callback, post_save_callback  # noqa
