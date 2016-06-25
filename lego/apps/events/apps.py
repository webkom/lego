from django.apps import AppConfig
from django.db.models.signals import post_save


class EventsConfig(AppConfig):
    name = 'lego.apps.events'

    def ready(self):
        from lego.apps.events.models import Event
        from lego.apps.events.signals import event_save_callback
        post_save.connect(event_save_callback, sender=Event)
