from django.apps import AppConfig

from .analytics_client import setup_analytics


class StatsConfig(AppConfig):
    name = "lego.apps.stats"
    verbose_name = "Stats"

    def ready(self):
        super().ready()
        setup_analytics()

        from .signals import post_delete_callback, post_save_callback  # noqa
