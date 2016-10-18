from lego import celery_app
from lego.apps.events.models import Event


class EventRegister(celery_app.Task):

    @classmethod
    def create_registration(cls, event_id, user):
        task = cls()
        task.delay(event_id, user)

    def run(self, event_id, user):
        event = Event.objects.get(pk=event_id)
        event.register(user)
