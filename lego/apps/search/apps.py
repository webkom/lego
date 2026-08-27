from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class SearchConfig(AppConfig):
    name = "lego.apps.search"
    verbose_name = "Search"

    def ready(self) -> None:
        super().ready()
        # This magic executes modules named search_indexes in every installed app. Search
        # indexes are registered this way.
        autodiscover_modules("search_indexes")
