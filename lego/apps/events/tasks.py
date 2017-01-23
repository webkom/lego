import stripe
from django.db import IntegrityError, transaction
from redis.exceptions import LockError
from structlog import get_logger

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.models import Registration
from lego.apps.events.serializers import StripeObjectSerializer

from .websockets import notify_event_registration, notify_failed_registration

log = get_logger()


@celery_app.task(serializer='json', bind=True)
def async_register(self, registration_id):
    registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            registration.event.register(registration)
            transaction.on_commit(
                lambda: notify_event_registration('SOCKET_REGISTRATION', registration)
            )
    except LockError as e:
        log.error('registration_cache_lock_error', exception=e, registration=registration)
        raise self.retry(exc=e)
    except (ValueError, IntegrityError) as e:
        log.error('registration_error', exception=e, registration=registration)
        registration.status = constants.FAILURE_REGISTER
        registration.save()
        notify_failed_registration('SOCKET_REGISTRATION_FAILED', registration)


@celery_app.task(serializer='json', bind=True)
def async_unregister(self, registration_id):
    registration = Registration.objects.get(id=registration_id)
    pool = registration.pool
    try:
        with transaction.atomic():
            registration.event.unregister(registration)
            transaction.on_commit(
                lambda: notify_event_registration('SOCKET_UNREGISTRATION', registration, pool.id)
            )
    except LockError as e:
        log.error('unregistration_cache_lock_error', exception=e, registration=registration)
        self.retry(exc=e)
    except IntegrityError as e:
        log.error('unregistration_error', exception=e, registration=registration)
        registration.status = constants.FAILURE_UNREGISTER
        registration.save()
        notify_failed_registration('SOCKET_REGISTRATION_FAILED', registration)


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
