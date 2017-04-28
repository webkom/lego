from django.apps import AppConfig


class StatsConfig(AppConfig):
    name = 'lego.apps.stats'
    verbose_name = 'Stats'

    def ready(self):
        super().ready()
        pass
