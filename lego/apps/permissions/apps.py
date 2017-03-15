from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class PermissionConfig(AppConfig):
    name = 'lego.apps.permissions'
    verbose_name = 'Permissions'

    def ready(self):
        super().ready()
        """
        This magic executes modules named permission_indexes in every installed app.
        Permissions indexes are registered this way.
        """

        autodiscover_modules('permissions')
