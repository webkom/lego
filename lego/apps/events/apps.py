from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save


class EventsConfig(AppConfig):
    name = 'lego.apps.events'

    def ready(self):
        if not settings.TESTING:
            from lego.apps.events.models import Event
            from lego.apps.events.signals import event_save_callback
            post_save.connect(event_save_callback, sender=Event)
