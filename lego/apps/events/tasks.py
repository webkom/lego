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
from lego.apps.feed.registry import get_handler

from .websockets import notify_event_registration, notify_user_registration

log = get_logger()


class AsyncRegister(celery_app.Task):
    serializer = 'json'
    default_retry_delay = 5
    registration = None

    def on_failure(self, *args):
        if self.request.retries == self.max_retries:
            self.registration.status = constants.FAILURE_REGISTER
            self.registration.save()
            notify_user_registration(constants.SOCKET_PAYMENT_FAILURE, self.registration)


class Payment(celery_app.Task):
    serializer = 'json'
    default_retry_delay = 5
    registration = None

    def on_retry(self, *args):
        notify_user_registration(
            constants.SOCKET_PAYMENT_FAILURE, self.registration,
            f'Payment failed, retrying #{self.request.retries+1}'
        )

    def on_failure(self, return_value, *args):
        if self.request.retries == self.max_retries:
            if return_value.json_body:
                error = return_value.json_body['error']
                self.registration.charge_id = error['charge']
                self.registration.charge_status = error['code']
                self.registration.save()
                notify_user_registration(
                    constants.SOCKET_PAYMENT_FAILURE, self.registration, error['message']
                )
            else:
                self.registration.charge_status = constants.PAYMENT_FAILURE
                self.registration.save()
                notify_user_registration(
                    constants.SOCKET_PAYMENT_FAILURE, self.registration, 'Payment failed'
                )
            # TODO: Notify about payment failure!


@celery_app.task(base=AsyncRegister, bind=True)
def async_register(self, registration_id):
    self.registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            self.registration.event.register(self.registration)
            transaction.on_commit(lambda: notify_event_registration(
                constants.SOCKET_REGISTRATION_SUCCESS, self.registration
            ))
    except LockError as e:
        log.error(
            'registration_cache_lock_error', exception=e, registration_id=self.registration.id
        )
        raise self.retry(exc=e, max_retries=3)
    except (ValueError, IntegrityError) as e:
        log.error('registration_error', exception=e, registration_id=self.registration.id)
        raise self.retry(exc=e, max_retries=3)


@celery_app.task(serializer='json', bind=True, default_retry_delay=30)
def async_unregister(self, registration_id):
    registration = Registration.objects.get(id=registration_id)
    pool = registration.pool
    try:
        with transaction.atomic():
            registration.event.unregister(registration)
            transaction.on_commit(lambda: notify_event_registration(
                constants.SOCKET_UNREGISTRATION_SUCCESS, registration, pool.id
            ))
    except LockError as e:
        log.error('unregistration_cache_lock_error', exception=e, registration_id=registration.id)
        raise self.retry(exc=e, max_retries=3)
    except IntegrityError as e:
        log.error('unregistration_error', exception=e, registration_id=registration.id)
        registration.status = constants.FAILURE_UNREGISTER
        registration.save()
        notify_user_registration(constants.SOCKET_UNREGISTRATION_FAILURE, registration)


@celery_app.task(base=Payment, bind=True)
def async_payment(self, registration_id, token):
    self.registration = Registration.objects.get(id=registration_id)
    event = self.registration.event
    try:
        response = stripe.Charge.create(
            amount=event.get_price(self.registration.user),
            currency='NOK',
            source=token,
            description=event.slug,
            metadata={
                'EVENT_ID': event.id,
                'USER': self.registration.user.full_name,
                'EMAIL': self.registration.user.email
            }
        )
        return response
        # TODO: Notify payment succeeded
    except stripe.error.CardError as e:
        raise self.retry(exc=e)
    except stripe.error.InvalidRequestError as e:
        log.error('invalid_request', exception=e, registration_id=self.registration.id)
        self.registration.charge_status = e.json_body['error']['type']
        self.registration.save()
        notify_user_registration(
            constants.SOCKET_PAYMENT_FAILURE, self.registration, 'Invalid request'
        )
    except stripe.error.StripeError as e:
        log.error('stripe_error', exception=e, registration_id=self.registration.id)
        raise self.retry(exc=e)


@celery_app.task(serializer='json', bind=True)
def registration_save(self, result, registration_id):
    try:
        registration = Registration.objects.get(id=registration_id)
        registration.charge_id = result['id']
        registration.charge_amount = result['amount']
        registration.charge_status = result['status']
        registration.save()
        notify_user_registration(constants.SOCKET_PAYMENT_SUCCESS, registration)
    except IntegrityError as e:
        log.error('registration_save_error', exception=e, registration_id=registration_id)
        raise self.retry(exc=e)


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
        # TODO: Notify websockets based on event.type


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


@celery_app.task(serializer='json')
def notify_user_when_payment_overdue():
    time = timezone.now()
    events = Event.objects.filter(
        payment_due_date__range=(time - timedelta(days=7), time), is_priced=True
    ).exclude(registrations=None).prefetch_related('registrations')
    for event in events:
        for registration in event.registrations.all():
            if registration.should_notify(time):
                get_handler(Registration).handle_payment_overdue(registration)
