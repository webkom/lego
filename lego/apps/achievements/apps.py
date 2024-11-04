from django.apps import AppConfig
from django.db.models.signals import post_save


class AchievementsConfig(AppConfig):
    name = "lego.apps.achievements"

    def ready(self):
        from lego.apps.achievements.signals import notify_on_achievement_callback
        from lego.apps.achievements.models import Achievement

        post_save.connect(
            notify_on_achievement_callback, sender=Achievement
        )
