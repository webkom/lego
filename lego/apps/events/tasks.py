from datetime import timedelta

import stripe
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils import timezone
from redis.exceptions import LockError
from structlog import get_logger

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.models import Event, Registration

from .websockets import notify_event_registration, notify_user_registration

log = get_logger()


@celery_app.task(serializer='json', bind=True, default_retry_delay=30)
def async_register(self, registration_id):
    registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            registration.event.register(registration)
            transaction.on_commit(
                lambda: notify_event_registration('SOCKET_REGISTRATION', registration)
            )
    except LockError as e:
        log.error('registration_cache_lock_error', exception=e, registration_id=registration.id)
        raise self.retry(exc=e, max_retries=3)
    except (ValueError, IntegrityError) as e:
        log.error('registration_error', exception=e, registration_id=registration.id)
        registration.status = constants.FAILURE_REGISTER
        registration.save()
        notify_user_registration('SOCKET_REGISTRATION_FAILED', registration)


@celery_app.task(serializer='json', bind=True, default_retry_delay=30)
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
        log.error('unregistration_cache_lock_error', exception=e, registration_id=registration.id)
        self.retry(exc=e, max_retries=3)
    except IntegrityError as e:
        log.error('unregistration_error', exception=e, registration_id=registration.id)
        registration.status = constants.FAILURE_UNREGISTER
        registration.save()
        notify_user_registration('SOCKET_REGISTRATION_FAILED', registration)


@celery_app.task(serializer='json', bind=True, default_retry_delay=60)
def async_payment(self, registration_id, token):
    registration = Registration.objects.get(id=registration_id)
    event = registration.event
    try:
        response = stripe.Charge.create(
            amount=event.get_price(registration.user),
            currency='NOK',
            source=token,
            description=event.slug,
            metadata={
                'EVENT_ID': event.id,
                'USER': registration.user.full_name,
                'EMAIL': registration.user.email
            }
        )
        registration.charge_id = response.id
        registration.charge_amount = response.amount
        registration.charge_status = response.status
        registration.save()
        notify_user_registration('SOCKET_PAYMENT', registration)
        # Notify by mail that payment succeeded
    except stripe.error.CardError as e:
        self.retry(exc=e)
        notify_user_registration('SOCKET_PAYMENT_FAILED', registration, 'Card declined')
    except stripe.error.InvalidRequestError as e:
        log.error('invalid_request', exception=e, registration_id=registration.id)
        self.retry(exc=e)
        notify_user_registration('SOCKET_PAYMENT_FAILED', registration, 'Invalid request')
    except stripe.error.StripeError as e:
        log.error('stripe_error', exception=e, registration_id=registration.id)
        self.retry(exc=e)
        notify_user_registration('SOCKET_PAYMENT_FAILED', registration, 'Payment failed')
        # Notify by mail that payment failed


@celery_app.task(serializer='json')
def stripe_webhook_event(event_id, event_type):
    from lego.apps.events.serializers import StripeObjectSerializer
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


@celery_app.task(serializer='json')
def check_events_for_registrations_with_expired_penalties():
    events = Event.objects.filter(start_time__gte=timezone.now()).exclude(registrations=None)
    for event in events:
        with cache.lock(f'event_lock-{event.id}'):
            if event.waiting_registrations.exists():
                for pool in event.pools.all():
                    if pool.is_activated and not pool.is_full:
                        for i in range(event.waiting_registrations.count()):
                            event.check_for_bump_or_rebalance(pool)
                            if pool.is_full:
                                break


@celery_app.task(serializer='json')
def bump_waiting_users_to_new_pool():
    events = Event.objects.filter(start_time__gte=timezone.now()).exclude(registrations=None)
    for event in events:
        with cache.lock(f'event_lock-{event.id}'):
            if event.waiting_registrations.exists():
                for pool in event.pools.all():
                    if not pool.is_full:
                        act = pool.activation_date
                        now = timezone.now()
                        if not pool.is_activated and act < now + timedelta(minutes=35):
                            event.early_bump(pool)
                        elif pool.is_activated and act > now - timedelta(minutes=35):
                            event.early_bump(pool)
