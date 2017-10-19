from datetime import timedelta

import stripe
from django.db import IntegrityError, transaction
from django.utils import timezone
from redis.exceptions import LockError
from structlog import get_logger

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.exceptions import EventHasStarted, PoolCounterNotEqualToRegistrationCount
from lego.apps.events.models import Event, Registration
from lego.apps.events.serializers.registrations import StripeObjectSerializer
from lego.apps.events.websockets import (notify_event_registration, notify_user_payment,
                                         notify_user_registration)
from lego.apps.feed.registry import get_handler

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

    def on_failure(self, return_value, *args):
        if self.request.retries == self.max_retries:
            if return_value.json_body:
                error = return_value.json_body['error']
                self.registration.charge_id = error['charge']
                self.registration.charge_status = error['code']
                self.registration.save()
                notify_user_registration(
                    constants.SOCKET_PAYMENT_FAILURE, self.registration,
                    error_message=error['message']
                )
            else:
                self.registration.charge_status = constants.PAYMENT_FAILURE
                self.registration.save()
                notify_user_registration(
                    constants.SOCKET_PAYMENT_FAILURE, self.registration,
                    error_message='Payment failed'
                )


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
    except EventHasStarted as e:
        log.warn(
            'registration_tried_after_started', exception=e, registration_id=self.registration.id
        )
    except (ValueError, IntegrityError) as e:
        log.error('registration_error', exception=e, registration_id=self.registration.id)
        raise self.retry(exc=e, max_retries=3)


@celery_app.task(serializer='json', bind=True, default_retry_delay=30)
def async_unregister(self, registration_id):
    registration = Registration.objects.get(id=registration_id)
    pool_id = registration.pool_id
    try:
        with transaction.atomic():
            registration.event.unregister(registration)
            activation_time = registration.event.get_earliest_registration_time(registration.user)
            transaction.on_commit(lambda: notify_event_registration(
                constants.SOCKET_UNREGISTRATION_SUCCESS, registration,
                from_pool=pool_id, activation_time=activation_time
            ))
    except LockError as e:
        log.error('unregistration_cache_lock_error', exception=e, registration_id=registration.id)
        raise self.retry(exc=e, max_retries=3)
    except EventHasStarted as e:
        log.warn(
            'unregistration_tried_after_started', exception=e, registration_id=registration.id
        )
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
    except stripe.error.CardError as e:
        raise self.retry(exc=e)
    except stripe.error.InvalidRequestError as e:
        log.error('invalid_request', exception=e, registration_id=self.registration.id)
        self.registration.charge_status = e.json_body['error']['type']
        self.registration.save()
        notify_user_payment(
            constants.SOCKET_PAYMENT_FAILURE, self.registration, error_message='Invalid request'
        )
    except stripe.error.StripeError as e:
        log.error('stripe_error', exception=e, registration_id=self.registration.id)
        raise self.retry(exc=e)


@celery_app.task(serializer='json', bind=True)
def registration_payment_save(self, result, registration_id):
    try:
        registration = Registration.objects.get(id=registration_id)
        registration.charge_id = result['id']
        registration.charge_amount = result['amount']
        registration.charge_status = result['status']
        registration.save()
        notify_user_payment(
            constants.SOCKET_PAYMENT_SUCCESS, registration, success_message='Betaling gjennomført'
        )
    except IntegrityError as e:
        log.error('registration_save_error', exception=e, registration_id=registration_id)
        raise self.retry(exc=e)


@celery_app.task(serializer='json', bind=True)
def check_for_bump_on_pool_creation_or_expansion(self, event_id):
    """Task checking for bumps when event and pools are updated"""
    # Event is locked using the instance field "is_ready"
    event = Event.objects.get(pk=event_id)
    event.bump_on_pool_creation_or_expansion()
    event.is_ready = True
    event.save(update_fields=['is_ready'])


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
        # TODO: Notify websockets based on event.type


@celery_app.task(serializer='json')
def check_events_for_registrations_with_expired_penalties():
    events_ids = Event.objects.filter(
        start_time__gte=timezone.now()
    ).exclude(registrations=None).values_list(flat=True)
    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            if locked_event.waiting_registrations.exists():
                for pool in locked_event.pools.all():
                    if pool.is_activated and not pool.is_full:
                        for i in range(locked_event.waiting_registrations.count()):
                            locked_event.check_for_bump_or_rebalance(pool)
                            if pool.is_full:
                                break


@celery_app.task(serializer='json')
def bump_waiting_users_to_new_pool():
    events_ids = Event.objects.filter(start_time__gte=timezone.now()).exclude(
        registrations=None).values_list(flat=True)
    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            if locked_event.waiting_registrations.exists():
                for pool in locked_event.pools.all():
                    if not pool.is_full:
                        act = pool.activation_date
                        now = timezone.now()
                        if not pool.is_activated and act < now + timedelta(minutes=35):
                            locked_event.early_bump(pool)
                        elif pool.is_activated and act > now - timedelta(minutes=35):
                            locked_event.early_bump(pool)


@celery_app.task(serializer='json')
def notify_user_when_payment_overdue():
    time = timezone.now()
    events = Event.objects.filter(is_priced=True).exclude(
        payment_due_days=None, registrations=None
    ).prefetch_related('registrations')
    for event in events:
        for registration in event.registrations.all():
            if registration.should_notify(time):
                get_handler(Registration).handle_payment_overdue(registration)


@celery_app.task(serializer='json')
def check_that_pool_counters_match_registration_number():
    """
    Task that checks whether pools counters are in sync with number of registrations. We do not
    enforce this check for events that are merged, hence the merge_time filter, because
    incrementing the counter decreases the registration performance
    """
    events_ids = Event.objects.filter(
        start_time__gte=timezone.now(), merge_time__gte=timezone.now()
    ).values_list(flat=True)

    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            for pool in locked_event.pools.all():
                registration_count = pool.registrations.count()
                if pool.counter != registration_count:
                    log.critical('pool_counter_not_equal_registration_count', pool=pool)
                    raise PoolCounterNotEqualToRegistrationCount(pool, locked_event)
