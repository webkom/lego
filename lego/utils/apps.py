from django.apps import AppConfig

from . import metrics


class UtilsConfig(AppConfig):

    name = 'lego.utils'
    verbose_name = 'Utils'

    def ready(self):
        metrics.setup_pusher()
