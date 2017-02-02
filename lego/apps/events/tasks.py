import stripe
from django.core.cache import cache
from django.db import IntegrityError, transaction
from redis.exceptions import LockError
from structlog import get_logger

from lego import celery_app
from lego.apps.events import constants
from lego.apps.events.models import Event, Pool, Registration

from .websockets import notify_event_registration, notify_failed_registration

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
            if registration.event.heed_penalties:
                total_penalty_weight = registration.user.number_of_penalties()
                if total_penalty_weight >= 3:
                    penalties = registration.user.penalties.valid().order_by('created_at')
                    for penalty in penalties:
                        if total_penalty_weight - penalty.weight < 3:
                            expiration = penalty.exact_expiration
                            if registration.event.start_time > expiration:
                                async_bump_after_expired_penalties.apply_async(
                                    (registration.id), eta=expiration
                                )
                            return
                        total_penalty_weight -= penalty.weight

    except LockError as e:
        log.error('registration_cache_lock_error', exception=e, registration_id=registration.id)
        raise self.retry(exc=e, max_retries=3)
    except (ValueError, IntegrityError) as e:
        log.error('registration_error', exception=e, registration_id=registration.id)
        registration.status = constants.FAILURE_REGISTER
        registration.save()
        notify_failed_registration('SOCKET_REGISTRATION_FAILED', registration)


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
        notify_failed_registration('SOCKET_REGISTRATION_FAILED', registration)


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


@celery_app.task(serializer='json', bind=True, default_retry_delay=30)
def async_bump_after_expired_penalties(self, registration_id):
    """
    Tries to bump a user that had 3 penalties at registration, but the penalties
    expire before the event starts. Only does something if there is a free slot at the time.
    :param registration_id: id of registration to be bumped.
    :return:
    """
    registration = Registration.objects.get(id=registration_id)
    user = registration.user
    event = registration.event
    try:
        with transaction.atomic():
            if not (event.is_full or user.number_of_penalties >= 3) and not registration.pool:
                with cache.lock(f'event_lock-{self.id}', timeout=20):
                    """ This is a simplified version of the register method,
                    without a lot of unneeded checks """
                    if event.is_merged:
                        event.check_for_bump_or_rebalance()

                    possible_pools = event.get_possible_pools(user)
                    if len(possible_pools) == 1 and event.pools.count() == 1:
                        event.check_for_bump_or_rebalance(possible_pools[0])

                    open_pools = event.calculate_full_pools(possible_pools)[1]
                    if not open_pools:
                        return
                    elif len(open_pools) == 1:
                        event.check_for_bump_or_rebalance(open_pools[0])
                    else:
                        exclusive_pools = event.find_most_exclusive_pools(open_pools)
                        if len(exclusive_pools) == 1:
                            event.check_for_bump_or_rebalance(exclusive_pools[0])
                        else:
                            chosen_pool = event.select_highest_capacity(exclusive_pools)
                            event.check_for_bump_or_rebalance(chosen_pool)
    except LockError as e:
        log.error(
            'expired_penalty_bump_cache_lock_error', exception=e, registration_id=registration.id
        )
        self.retry(exc=e, max_retries=3)
    except IntegrityError as e:
        log.error('expired_penalty_bump_error', exception=e, registration_id=registration.id)


@celery_app.task(serializer='json', bind=True, default_retry_delay=30)
def async_bump_on_pool_activation(self, event_id, pool_id):
    """
    Tries to bump users if a new pool opens while there are users in the waiting list.
    :param event_id: Duh.
    :param pool_id: Id of the new pool.
    :return:
    """
    event = Event.objects.get(id=event_id)
    pool = Pool.objects.get(id=pool_id)
    try:
        with transaction.atomic():
            if event.waiting_registrations.exists():
                with cache.lock(f'event_lock-{self.id}', timeout=20):
                    for i in range(event.waiting_registrations.count()):
                        event.check_for_bump_or_rebalance(pool)
    except LockError as e:
        log.error(
            'pool_activation_bump_cache_lock_error', exception=e, event_id=event.id, pool_id=pool.id
        )
        self.retry(exc=e, max_retries=3)
    except IntegrityError as e:
        log.error('pool_activation_bump_error', exception=e, event_id=event.id, pool_id=pool.id)
