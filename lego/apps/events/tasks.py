from lego import celery_app


class EventRegister(celery_app.Task):

    @classmethod
    def async_register(cls, event_id, user_id):
        task = cls()
        task.delay(event_id, user_id)

    def run(self, event_id, user_id):
        from lego.apps.events.models import Event
        from lego.apps.users.models import User
        event = Event.objects.get(pk=event_id)
        user = User.objects.get(pk=user_id)
        event.register(user)


class EventUnregister(celery_app.Task):

    @classmethod
    def async_unregister(cls, event_id, user_id):
        task = cls()
        task.delay(event_id, user_id)

    def run(self, event_id, user_id):
        from lego.apps.events.models import Event, User
        event = Event.objects.get(pk=event_id)
        user = User.objects.get(pk=user_id)
        event.unregister(user)
