from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'lego.utils'
    verbose_name = 'Utils'

    def ready(self):
        super().ready()
        from .signals import post_save_callback, post_delete_callback  # noqa
