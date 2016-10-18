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
    def async_bump(cls, event, pool):
        task = cls()
        task.delay(event, pool)

    def run(self, event_id, pool_id):
        from lego.apps.events.models import Event, Pool
        event = Event.objects.get(pk=event_id)
        pool = Pool.objects.get(pk=pool_id)
        event.check_for_bump_or_rebalance(pool)
