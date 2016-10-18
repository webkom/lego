from lego import celery_app


class EventRegister(celery_app.Task):

    @classmethod
    def async_register(cls, event_id, user):
        task = cls()
        task.delay(event_id, user)

    def run(self, event_id, user):
        from lego.apps.events.models import Event
        event = Event.objects.get(pk=event_id)
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
