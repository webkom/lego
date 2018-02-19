from django.apps import AppConfig


class FeedsConfig(AppConfig):
    name = 'lego.apps.feeds'
    verbose_name = 'Feeds'

    def ready(self):
        super().ready()
        """
        Import signals to start listening for events
        """
        from .verbs import verbs  # noqa
