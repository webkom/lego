from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'lego.apps.users'
    verbose_name = 'Users'

    def ready(self):
        super().ready()
        from .signals import post_save_callback  # noqa
