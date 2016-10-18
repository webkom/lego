from lego import celery_app


class EventRegister(celery_app.Task):

    @classmethod
    def create_registration(cls, event_id, user):
        task = cls()
        task.delay(event_id, user)

    def run(self, event_id, user):
        from lego.apps.events.models import Event
        event = Event.objects.get(pk=event_id)
        event.register(user)
