import stripe
from django.db import IntegrityError, transaction

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.models import Registration
from lego.apps.events.serializers import StripeObjectSerializer

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


@celery_app.task(serializer='json')
def stripe_webhook_event(event_id, event_type):
    if event_type in ['charge.failed', 'charge.refunded', 'charge.succeeded']:
        event = stripe.Event.retrieve(event_id)
        serializer = StripeObjectSerializer(data=event.data['object'])
        serializer.is_valid(raise_exception=True)

        registration = Registration.objects.get(charge_id=serializer.data['id'])
        registration.charge_amount = serializer.data['amount']
        registration.charge_amount_refunded = serializer.data['amount_refunded']
        registration.charge_status = serializer.data['status']
        registration.save()

        # Notify websockets based on event.type
