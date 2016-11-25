from django.db import IntegrityError, transaction

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.models import Registration

from .websockets import notify_registration, notify_unregistration


@celery_app.task(serializer='json')
def async_register(registration_id):

    registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            registration.event.register(registration)
            transaction.on_commit(lambda: notify_registration('SOCKET_REGISTRATION', registration))
    except (ValueError, IntegrityError):
        registration.status = constants.FAILURE_REGISTER
        registration.save()
        # Notify websockets with failure


@celery_app.task(serializer='json')
def async_unregister(registration_id):
    registration = Registration.objects.get(id=registration_id)
    pool = registration.pool
    try:
        with transaction.atomic():
            registration.event.unregister(registration)
            transaction.on_commit(lambda: notify_unregistration('SOCKET_UNREGISTRATION',
                                                                registration, pool.id))
    except IntegrityError:
        registration.status = constants.FAILURE_UNREGISTER
        registration.save()
        # Notify websockets with failure
