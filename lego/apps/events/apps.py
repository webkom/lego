from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save


class EventsConfig(AppConfig):
    name = "lego.apps.events"

    def ready(self):
        from lego.apps.events.models import Event, Registration
        from lego.apps.events.signals import (
            check_achievement_on_registration_callback,
            event_save_callback,
        )

        if not settings.TESTING:
            post_save.connect(event_save_callback, sender=Event)

        post_save.connect(
            check_achievement_on_registration_callback, sender=Registration
        )
