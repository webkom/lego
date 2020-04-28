from django.apps import AppConfig

from health_check.plugins import plugin_dir

from lego.apps.healthchecks.backends import (
    HealthCheckArticlesBackend,
    HealthCheckEventsBackend,
    HealthCheckGroupsBackend,
    HealthCheckPagesBackend,
    HealthCheckUsersBackend,
)


class HealthChecksConfig(AppConfig):
    name = "lego.apps.healthchecks"

    def ready(self):
        plugin_dir.register(HealthCheckArticlesBackend)
        plugin_dir.register(HealthCheckEventsBackend)
        plugin_dir.register(HealthCheckGroupsBackend)
        plugin_dir.register(HealthCheckPagesBackend)
        plugin_dir.register(HealthCheckUsersBackend)
