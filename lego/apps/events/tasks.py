from django.db import IntegrityError, transaction

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.models import Registration


@celery_app.task(serializer='json')
def async_register(registration_id):

    registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            registration.event.register(registration)
            # Notify websockets with success and send mail with on_commit
    except (ValueError, IntegrityError):
        registration.status = constants.STATUS_FAILURE
        registration.save()
        # Notify websockets with failure


@celery_app.task(serializer='json')
def async_unregister(registration_id):
    registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            registration.event.unregister(registration)
    except IntegrityError:
        registration.status = constants.STATUS_FAILURE
        registration.save()
        # Notify websockets with failure
