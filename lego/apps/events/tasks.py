import uuid
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

import stripe
from celery.canvas import chain
from structlog import get_logger

from lego import celery_app
from lego.apps.action_handlers.events import handle_event
from lego.apps.events import constants
from lego.apps.events.exceptions import (
    EventHasClosed,
    PoolCounterNotEqualToRegistrationCount,
    WebhookDidNotFindRegistration,
)
from lego.apps.events.models import Event, Registration
from lego.apps.events.notifications import (
    EventPaymentOverdueCreatorNotification,
    EventPaymentOverduePenaltyNotification,
)
from lego.apps.events.serializers.registrations import (
    StripeChargeSerializer,
    StripePaymentIntentSerializer,
)
from lego.apps.events.websockets import (
    notify_event_registration,
    notify_user_payment,
    notify_user_payment_error,
    notify_user_payment_initiated,
    notify_user_registration,
)
from lego.apps.users.constants import PENALTY_TYPES, PENALTY_WEIGHTS
from lego.apps.users.models import Penalty
from lego.utils.tasks import AbakusTask

log = get_logger()


class AsyncRegister(AbakusTask):
    serializer = "json"
    default_retry_delay = 5
    registration = None

    def on_failure(self, *args):
        if self.request.retries == self.max_retries:
            with transaction.atomic():
                registration = Registration.objects.select_for_update().get(
                    id=self.registration.id
                )
                if registration.status != constants.SUCCESS_REGISTER:
                    registration.status = constants.FAILURE_REGISTER
                    registration.save()
            notify_user_registration(
                constants.SOCKET_REGISTRATION_FAILURE,
                self.registration,
                error_message="Registrering feilet",
            )


class Payment(AbakusTask):
    serializer = "json"
    default_retry_delay = 5
    registration = None

    def on_failure(self, return_value, *args):
        if self.request.retries == self.max_retries:
            if return_value.json_body:
                error = return_value.json_body["error"]
                notify_user_payment(
                    constants.SOCKET_INITIATE_PAYMENT_FAILURE,
                    self.registration,
                    error_message=error["message"],
                )
            else:
                notify_user_payment(
                    constants.SOCKET_INITIATE_PAYMENT_FAILURE,
                    self.registration,
                    error_message="Noe gikk galt med betalingen.",
                )


@celery_app.task(base=AsyncRegister, bind=True)
def async_register(self, registration_id, logger_context=None):
    self.setup_logger(logger_context)

    try:
        with transaction.atomic():
            self.registration = Registration.objects.select_for_update().get(
                id=registration_id
            )
            self.registration.event.register(self.registration)
            transaction.on_commit(
                lambda: notify_event_registration(
                    constants.SOCKET_REGISTRATION_SUCCESS, self.registration
                )
            )
        log.info("registration_success", registration_id=self.registration.id)
        if self.registration.can_pay:
            chain(
                async_initiate_payment.s(registration_id),
                save_and_notify_payment.s(registration_id),
            ).delay()

    except EventHasClosed as e:
        log.warn(
            "registration_tried_after_started",
            exception=e,
            registration_id=self.registration.id,
        )
    except (ValueError, IntegrityError) as e:
        log.error(
            "registration_error", exception=e, registration_id=self.registration.id
        )
        raise self.retry(exc=e, max_retries=3) from e


@celery_app.task(serializer="json", bind=True, base=AbakusTask, default_retry_delay=30)
def async_unregister(self, registration_id, logger_context=None):
    self.setup_logger(logger_context)

    registration = Registration.objects.get(id=registration_id)
    pool_id = registration.pool_id
    try:
        with transaction.atomic():
            registration.event.unregister(registration)
            activation_time = registration.event.get_earliest_registration_time(
                registration.user
            )
            transaction.on_commit(
                lambda: notify_event_registration(
                    constants.SOCKET_UNREGISTRATION_SUCCESS,
                    registration,
                    from_pool=pool_id,
                    activation_time=activation_time,
                )
            )
        if (
            registration.payment_intent_id
            and registration.payment_status != constants.PAYMENT_SUCCESS
        ):
            async_cancel_payment.delay(registration_id)
        log.info("unregistration_success", registration_id=registration.id)
    except EventHasClosed as e:
        log.warn(
            "unregistration_tried_after_started",
            exception=e,
            registration_id=registration.id,
        )
        registration.status = constants.FAILURE_UNREGISTER
        registration.save()
        notify_user_registration(
            constants.SOCKET_UNREGISTRATION_FAILURE,
            registration,
            error_message="Avregistrering er stengt",
        )
    except IntegrityError as e:
        log.error("unregistration_error", exception=e, registration_id=registration.id)
        registration.status = constants.FAILURE_UNREGISTER
        registration.save()
        notify_user_registration(
            constants.SOCKET_UNREGISTRATION_FAILURE,
            registration,
            error_message="Avregistrering feilet",
        )


@celery_app.task(base=AbakusTask, bind=True)
def async_retrieve_payment(self, registration_id, logger_context=None):
    """
    Task that retrieves an existing payment intents client_secret from Stripe.
    If the client_secret is provided, this is returned directly
    """
    self.registration = Registration.objects.get(id=registration_id)

    if self.registration.payment_intent_id is None:
        log.error(
            "Attempted to retrieve a non-existing payment intent",
            registration=self.registration.id,
        )
        raise ValueError("The payment intent does not exist")

    try:
        payment_intent = stripe.PaymentIntent.retrieve(
            self.registration.payment_intent_id
        )
        client_secret = payment_intent["client_secret"]
    except stripe.error.InvalidRequestError as e:
        log.error("invalid_request", exception=e, registration_id=self.registration.id)
        self.registration.payment_status = e.json_body["error"]["type"]
        self.registration.save()
    except stripe.error.StripeError as e:
        log.error("stripe_error", exception=e, registration_id=self.registration.id)
        raise self.retry(exc=e, max_retries=3) from e
    except stripe.error.APIConnectionError as e:
        log.error(
            "stripe_APIConnectionError",
            exception=e,
            registration_id=self.registration.id,
        )
        raise self.retry(exc=e, max_retries=3) from e
    except Exception as e:
        log.error(
            "Exception on creating a payment intent",
            exception=e,
            registration=self.registration.id,
        )
        raise self.retry(exc=e) from e

    # Check that the payment intent is not already confirmed
    # If so, update the payment status to reflect reality
    # See https://stripe.com/docs/api/payment_intents/object
    if payment_intent["status"] == constants.STRIPE_INTENT_SUCCEEDED:
        self.registration.payment_status = constants.PAYMENT_SUCCESS
        self.registration.payment_amount = payment_intent["amount"]
        self.registration.save()
        notify_user_payment_error(
            constants.SOCKET_PAYMENT_FAILURE,
            self.registration,
            success_message="Betaling feilet",
            payment_error="The payment is already successful",
        )
        return

    # If the payment is canceled in stripe and the webhook for some reason
    # did not go through, we update the registration to match this, and then
    # initiate a new payment.
    if payment_intent["status"] == constants.STRIPE_INTENT_CANCELED:
        self.registration.payment_status = constants.PAYMENT_CANCELED
        self.registration.payment_intent_id = None
        self.registration.payment_idempotency_key = None
        self.registration.save()
        chain(
            async_initiate_payment.s(self.registration.id),
            save_and_notify_payment.s(self.registration.id),
        ).delay()
        return

    notify_user_payment_initiated(
        constants.SOCKET_INITIATE_PAYMENT_SUCCESS,
        self.registration,
        success_message="Betaling påbegynt",
        client_secret=client_secret,
    )


@celery_app.task(base=Payment, bind=True)
def async_initiate_payment(self, registration_id, logger_context=None):
    """
    Task that creates a new Stripe payment intent. Stripe returns a payment_intent object. The
    client_secret is then needed to finish the payment on the client side.
    """
    self.setup_logger(logger_context)

    self.registration = Registration.objects.get(id=registration_id)
    event = self.registration.event

    if not self.registration.payment_idempotency_key:
        self.registration.payment_idempotency_key = uuid.uuid4()
        self.registration.save()

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=event.get_price(self.registration.user),
            receipt_email=self.registration.user.email,
            currency="NOK",
            description=event.slug,
            idempotency_key=str(self.registration.payment_idempotency_key),
            metadata={
                "EVENT_ID": event.id,
                "USER_ID": self.registration.user.id,
                "USER": self.registration.user.full_name,
                "EMAIL": self.registration.user.email,
            },
        )
        log.info(
            "stripe_payment_intent_create_success", registration_id=self.registration.id
        )

        return payment_intent

    except stripe.error.InvalidRequestError as e:
        log.error("invalid_request", exception=e, registration_id=self.registration.id)
        self.registration.payment_status = e.json_body["error"]["type"]
        self.registration.save()
    except stripe.error.StripeError as e:
        log.error("stripe_error", exception=e, registration_id=self.registration.id)
        raise self.retry(exc=e, max_retries=3) from e
    except stripe.error.APIConnectionError as e:
        log.error(
            "stripe_APIConnectionError",
            exception=e,
            registration_id=self.registration.id,
        )
        raise self.retry(exc=e, max_retries=3) from e
    except Exception as e:
        log.error(
            "Exception on creating a payment intent",
            exception=e,
            registration=self.registration.id,
        )
        raise self.retry(exc=e) from e


@celery_app.task(bind=True, base=AbakusTask)
def async_cancel_payment(self, registration_id, logger_context=None):
    """
    Cancel a Stripe payment intent connected to a users registration.
    """
    self.setup_logger(logger_context)

    registration = Registration.objects.get(id=registration_id)

    if registration.payment_intent_id is None:
        log.error(
            "Attempting to cancel a payment intent that does not exist",
            registration=registration.id,
        )
        raise ValueError("Payment intent does not exist")

    try:
        stripe.PaymentIntent.cancel(registration.payment_intent_id)
    except stripe.error.InvalidRequestError as e:
        log.error(
            "Exception when attempting to cancel a payment intent",
            exception=e,
            registration=registration.id,
        )


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def save_and_notify_payment(self, result, registration_id, logger_context=None):
    """
    Saves a users registration with new payment details and sends the stripe payment_intent
    client_secret to the client.
    Result is a stripe payment_intent
    """
    self.setup_logger(logger_context)

    try:
        registration = Registration.objects.get(id=registration_id)
        registration.payment_intent_id = result["id"]
        registration.payment_amount = result["amount"]
        registration.payment_intent_status = result["status"]
        registration.save()

    except IntegrityError as e:
        log.error(
            "registration_save_error", exception=e, registration_id=registration_id
        )
        raise self.retry(exc=e) from e

    notify_user_payment_initiated(
        constants.SOCKET_INITIATE_PAYMENT_SUCCESS,
        registration,
        success_message="Betaling påbegynt",
        client_secret=result["client_secret"],
    )


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def set_all_events_ready_and_bump(self, logger_context=None):
    """Task to bump all tasks to is_ready=True in case of error"""
    self.setup_logger(logger_context)

    # Find all events that are set to "is_ready=False" and are not awaiting automatic
    # celery task (have just been edited)
    now = timezone.now()
    corrupt_events = Event.objects.filter(is_ready=False).filter(
        updated_at__lt=now - timedelta(minutes=5)
    )
    for event in corrupt_events:
        check_for_bump_on_pool_creation_or_expansion(event.pk, logger_context)


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def check_for_bump_on_pool_creation_or_expansion(
    self, event_id: int, logger_context=None
):
    """Task checking for bumps when event and pools are updated"""
    self.setup_logger(logger_context)

    # Event is locked using the instance field "is_ready"
    event = Event.objects.get(pk=event_id)
    event.bump_on_pool_creation_or_expansion()
    event.is_ready = True
    event.save(update_fields=["is_ready"])


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def stripe_webhook_event(self, event_id, event_type, logger_context=None):
    """
    Task that handles webhook events from Stripe, and updates the users registration in accordance
    with the payment status.
    """
    self.setup_logger(logger_context)
    event = stripe.Event.retrieve(event_id)

    if event_type in [
        constants.STRIPE_EVENT_INTENT_SUCCESS,
        constants.STRIPE_EVENT_INTENT_PAYMENT_FAILED,
        constants.STRIPE_EVENT_INTENT_PAYMENT_CANCELED,
    ]:
        serializer = StripePaymentIntentSerializer(data=event.data["object"])
        serializer.is_valid(raise_exception=True)

        metadata = serializer.data["metadata"]
        registration = Registration.objects.filter(
            event_id=metadata["EVENT_ID"], user__id=metadata["USER_ID"]
        ).first()
        if not registration:
            log.error("stripe_webhook_error", event_id=event_id, metadata=metadata)
            raise WebhookDidNotFindRegistration(event_id, metadata)

        registration.payment_amount = serializer.data["amount"]
        # We update the payment status based on the stripe event type
        if event_type == constants.STRIPE_EVENT_INTENT_SUCCESS:
            registration.payment_status = constants.PAYMENT_SUCCESS
            notify_user_payment(
                constants.SOCKET_PAYMENT_SUCCESS,
                registration,
                success_message="Betaling godkjent",
            )
        elif event_type == constants.STRIPE_EVENT_INTENT_PAYMENT_FAILED:
            registration.payment_status = constants.PAYMENT_FAILURE
            notify_user_payment(
                constants.SOCKET_PAYMENT_FAILURE,
                registration,
                error_message="Betaling feilet",
            )
        elif event_type == constants.STRIPE_EVENT_INTENT_PAYMENT_CANCELED:
            registration.payment_status = constants.PAYMENT_CANCELED
            registration.payment_intent_id = None
            registration.payment_idempotency_key = None

        registration.save()

    elif event_type in [constants.STRIPE_EVENT_CHARGE_REFUNDED]:
        serializer = StripeChargeSerializer(data=event.data["object"])
        serializer.is_valid(raise_exception=True)

        metadata = serializer.data["metadata"]
        registration = Registration.objects.filter(
            event_id=metadata["EVENT_ID"], user__id=metadata["USER_ID"]
        ).first()
        if not registration:
            log.error("stripe_webhook_error", event_id=event_id, metadata=metadata)
            raise WebhookDidNotFindRegistration(event_id, metadata)

        registration.payment_status = constants.PAYMENT_SUCCESS
        registration.payment_amount_refunded = serializer.data["amount_refunded"]
        registration.save()

    log.info("stripe_webhook_received", event_id=event_id)


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def check_events_for_registrations_with_expired_penalties(self, logger_context=None):
    self.setup_logger(logger_context)

    events_ids = (
        Event.objects.filter(start_time__gte=timezone.now())
        .exclude(registrations=None)
        .values_list("id", flat=True)
    )
    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            if locked_event.waiting_registrations.exists():
                locked_pools = locked_event.pools.select_for_update().all()
                for pool in locked_pools:
                    if pool.is_activated and not pool.is_full:
                        for _ in range(locked_event.waiting_registrations.count()):
                            locked_event.check_for_bump_or_rebalance(pool)
                            if pool.is_full:
                                break


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def bump_waiting_users_to_new_pool(self, logger_context=None):
    self.setup_logger(logger_context)

    events_ids = (
        Event.objects.filter(start_time__gte=timezone.now())
        .exclude(registrations=None)
        .values_list("id", flat=True)
    )
    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            if locked_event.waiting_registrations.exists():
                locked_pools = locked_event.pools.select_for_update().all()
                for pool in locked_pools:
                    if not pool.is_full:
                        act = pool.activation_date
                        now = timezone.now()
                        if not pool.is_activated and act < now + timedelta(minutes=35):
                            locked_event.early_bump(pool)
                            log.info(
                                "early_bump_executed",
                                event_id=event_id,
                                pool_id=pool.id,
                            )
                        elif pool.is_activated and act > now - timedelta(minutes=35):
                            log.info(
                                "early_bump_executed",
                                event_id=event_id,
                                pool_id=pool.id,
                            )
                            locked_event.early_bump(pool)


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def notify_user_when_payment_soon_overdue(self, logger_context=None):
    self.setup_logger(logger_context)

    time = timezone.now()
    events = (
        Event.objects.filter(
            payment_due_date__range=(
                time - timedelta(days=2),
                time + timedelta(days=3),
            ),
            is_priced=True,
            use_stripe=True,
        )
        .exclude(registrations=None)
        .prefetch_related("registrations")
    )
    for event in events:
        for registration in event.registrations.exclude(pool=None):
            if registration.should_notify(time):
                log.info(
                    "registration_notified_overdue_payment",
                    event_id=event.id,
                    registration_id=registration.id,
                )
                handle_event(registration, "payment_overdue")


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def notify_event_creator_when_payment_overdue(self, logger_context=None):
    self.setup_logger(logger_context)

    time = timezone.now()
    events = (
        Event.objects.filter(
            payment_due_date__lte=time,
            is_priced=True,
            use_stripe=True,
            end_time__gte=time,
        )
        .exclude(registrations=None)
        .prefetch_related("registrations")
    )
    for event in events:
        registrations_due = (
            event.registrations.exclude(pool=None)
            .exclude(
                payment_status__in=[constants.PAYMENT_MANUAL, constants.PAYMENT_SUCCESS]
            )
            .prefetch_related("user")
        )
        if registrations_due:
            users = [
                {
                    "name": registration.user.get_full_name(),
                    "email": registration.user.email,
                }
                for registration in registrations_due
            ]
            notification = EventPaymentOverdueCreatorNotification(
                event.created_by, event=event, users=users
            )
            notification.notify()
            log.info(
                "event_creator_notified_of_overdue_payments",
                event_id=event.id,
                creator=event.created_by,
            )


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def handle_overdue_payment(self, logger_context=None):
    """
    Task that automatically assigns penalty, unregisters user from event
    and notifies them when payment is overdue.
    """

    self.setup_logger(logger_context)

    time = timezone.now()
    events = (
        Event.objects.filter(
            payment_due_date__lte=time,
            is_priced=True,
            use_stripe=True,
            end_time__gte=time,
        )
        .exclude(registrations=None)
        .prefetch_related("registrations")
    )
    for event in events:
        overdue_registrations = (
            event.registrations.exclude(pool=None)
            .exclude(
                payment_status__in=[constants.PAYMENT_MANUAL, constants.PAYMENT_SUCCESS]
            )
            .prefetch_related("user")
        )
        if overdue_registrations:
            for registration in overdue_registrations:
                user = registration.user

                if not user.penalties.filter(source_event=event).exists():
                    Penalty.objects.create(
                        user=user,
                        reason=f"Betalte ikke for {event.title} i tide.",
                        weight=PENALTY_WEIGHTS.PAYMENT_OVERDUE,
                        source_event=event,
                        type=PENALTY_TYPES.PAYMENT,
                    )

                event.unregister(
                    registration,
                    # Needed to not give default penalty
                    admin_unregistration_reason="Automated unregister",
                )

                notification = EventPaymentOverduePenaltyNotification(
                    user=user,
                    event=event,
                )
                notification.notify()
                log.info(
                    "user_is_given_penalty_is_unregistered_and_notified",
                    event_id=event.id,
                    registration=registration,
                )


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def check_that_pool_counters_match_registration_number(self, logger_context=None):
    """
    Task that checks whether pools counters are in sync with number of registrations. We do not
    enforce this check for events that are merged, hence the merge_time filter, because
    incrementing the counter decreases the registration performance
    """
    self.setup_logger(logger_context)

    events_ids = Event.objects.filter(
        Q(start_time__gte=timezone.now()),
        Q(merge_time__gte=timezone.now()) | Q(merge_time__isnull=True),
    ).values_list("id", flat=True)

    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            locked_pools = locked_event.pools.select_for_update().all()
            for pool in locked_pools:
                registration_count = pool.registrations.count()
                if pool.counter != registration_count:
                    log.critical("pool_counter_not_equal_registration_count", pool=pool)
                    raise PoolCounterNotEqualToRegistrationCount(
                        pool, registration_count, locked_event
                    )
