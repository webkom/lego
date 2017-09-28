from django.apps import AppConfig
from django.conf import settings


class UsersConfig(AppConfig):
    name = 'lego.apps.users'
    verbose_name = 'Users'

    def ready(self):
        if not settings.TESTING:
            from .signals import post_save_callback  # noqa
