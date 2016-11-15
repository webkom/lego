from lego import celery_app


@celery_app.task(serializer='pickle')
def async_register(event_id, user_id):
    from lego.apps.events.models import Event
    from lego.apps.users.models import User
    event = Event.objects.get(pk=event_id)
    user = User.objects.get(pk=user_id)
    event.register(user)


@celery_app.task(serializer='pickle')
def async_unregister(event_id, user_id):
    from lego.apps.events.models import Event
    from lego.apps.users.models import User
    event = Event.objects.get(pk=event_id)
    user = User.objects.get(pk=user_id)
    event.unregister(user)
