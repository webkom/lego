from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class ActionHandlersConfig(AppConfig):
    name = 'lego.apps.action_handlers'
    verbose_name = 'ActionHandlers'

    def ready(self):
        super().ready()
        autodiscover_modules('action_handlers')

        # Initialize signals
        from .signals import post_delete_callback, post_save_callback  # noqa
