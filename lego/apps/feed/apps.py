from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class FeedConfig(AppConfig):
    name = 'lego.apps.feed'
    verbose_name = "Feed"

    def ready(self):
        super().ready()
        """
        Import signals to start listening for events
        """
        autodiscover_modules('feed_handlers')
        from .signals import post_save_callback, post_delete_callback  # noqa
