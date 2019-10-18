from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

import stripe
from celery import chain
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
from lego.apps.events.notifications import EventPaymentOverdueCreatorNotification
from lego.apps.events.serializers.registrations import (
    StripeChargeSerializer,
    StripePaymentIntentSerializer,
)
from lego.apps.events.websockets import (
    notify_event_registration,
    notify_user_payment,
    notify_user_payment_initiated,
    notify_user_registration,
)
from lego.utils.tasks import AbakusTask

log = get_logger()


class AsyncRegister(AbakusTask):
    serializer = "json"
    default_retry_delay = 5
    registration = None

    def on_failure(self, *args):
        if self.request.retries == self.max_retries:
            self.registration.status = constants.FAILURE_REGISTER
            self.registration.save()
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

    self.registration = Registration.objects.get(id=registration_id)
    try:
        with transaction.atomic():
            self.registration.event.register(self.registration)
            transaction.on_commit(
                lambda: notify_event_registration(
                    constants.SOCKET_REGISTRATION_SUCCESS, self.registration
                )
            )
        log.info("registration_success", registration_id=self.registration.id)
        if self.registration.event.is_priced and self.event.use_stripe:
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
        raise self.retry(exc=e, max_retries=3)


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
        async_cancel_payment.s(registration_id).delay()
        log.info("unregistration_success", registration_id=registration.id)
    except EventHasClosed as e:
        log.warn(
            "unregistration_tried_after_started",
            exception=e,
            registration_id=registration.id,
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
def async_retrieve_payment(
    self, registration_id, client_secret=None, logger_context=None
):
    """
    Task that retrieves an existing payment intents client_secret from Stripe.
    If the client_secret is provided, this is returned directly
    """
    self.registration = Registration.objects.get(id=registration_id)

    if client_secret is None:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(
                self.registration.payment_intent_id
            )
            client_secret = payment_intent["client_secret"]
        except stripe.error.InvalidRequestError as e:
            log.error(
                "invalid_request", exception=e, registration_id=self.registration.id
            )
            self.registration.payment_status = e.json_body["error"]["type"]
            self.registration.save()
        except stripe.error.StripeError as e:
            log.error("stripe_error", exception=e, registration_id=self.registration.id)
            raise self.retry(exc=e, max_retries=3)
        except stripe.error.APIConnectionError as e:
            log.error(
                "stripe_APIConnectionError",
                exception=e,
                registration_id=self.registration.id,
            )
            raise self.retry(exc=e, max_retries=3)
        except Exception as e:
            log.error(
                "Exception on creating a payment intent",
                exception=e,
                registration=self.registration.id,
            )
            raise self.retry(exc=e)

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
    client_secret is then needed to finsish the payment on frontend.
    """
    self.setup_logger(logger_context)

    self.registration = Registration.objects.get(id=registration_id)
    event = self.registration.event
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=event.get_price(self.registration.user),
            receipt_email=self.registration.user.email,
            currency="NOK",
            description=event.slug,
            idempotency_key=self.registration.id,
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
        raise self.retry(exc=e, max_retries=3)
    except stripe.error.APIConnectionError as e:
        log.error(
            "stripe_APIConnectionError",
            exception=e,
            registration_id=self.registration.id,
        )
        raise self.retry(exc=e, max_retries=3)
    except Exception as e:
        log.error(
            "Exception on creating a payment intent",
            exception=e,
            registration=self.registration.id,
        )
        raise self.retry(exc=e)


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
        raise self.retry(exc=e)

    notify_user_payment_initiated(
        constants.SOCKET_INITIATE_PAYMENT_SUCCESS,
        registration,
        success_message="Betaling påbegynt",
        client_secret=result["client_secret"],
    )


@celery_app.task(serializer="json", bind=True, base=AbakusTask)
def check_for_bump_on_pool_creation_or_expansion(self, event_id, logger_context=None):
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

    if event_type in ["payment_intent.payment_failed", "payment_intent.succeeded"]:

        event = stripe.Event.retrieve(event_id)
        if event_type == "charge.refunded":
            serializer = StripeChargeSerializer(data=event.data["object"])
        else:
            serializer = StripePaymentIntentSerializer(data=event.data["object"])
        serializer.is_valid(raise_exception=True)

        metadata = serializer.data["metadata"]
        registration = Registration.objects.filter(
            event_id=metadata["EVENT_ID"], user__email=metadata["EMAIL"]
        ).first()
        if not registration:
            log.error("stripe_webhook_error", event_id=event_id, metadata=metadata)
            raise WebhookDidNotFindRegistration(event_id, metadata)

        if event_type == "charge.refunded":
            registration.payment_amount_refunded = serializer.data["amount_refunded"]
        else:
            registration.payment_intent_id = serializer.data["id"]
            registration.payment_amount = serializer.data["amount"]
            # We update the payment status based on the stripe event type
            if event_type == "payment_intent.succeeded":
                registration.payment_status = constants.PAYMENT_SUCCESS
            elif event_type == "payment_intent.payment_failed":
                registration.payment_status = constants.PAYMENT_FAILURE
            registration.save()

        if event_type == "payment_intent.succeeded":
            notify_user_payment(
                constants.SOCKET_PAYMENT_SUCCESS,
                registration,
                success_message="Betaling godkjent",
            )
        elif event_type == "payment_intent.payment_failed":
            notify_user_payment(
                constants.SOCKET_PAYMENT_FAILURE,
                registration,
                error_message="Betaling feilet",
            )

        log.info(
            "stripe_webhook_received",
            event_id=event_id,
            registration_id=registration.id,
        )


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
                for pool in locked_event.pools.all():
                    if pool.is_activated and not pool.is_full:
                        for i in range(locked_event.waiting_registrations.count()):
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
                for pool in locked_event.pools.all():
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
def check_that_pool_counters_match_registration_number(self, logger_context=None):
    """
    Task that checks whether pools counters are in sync with number of registrations. We do not
    enforce this check for events that are merged, hence the merge_time filter, because
    incrementing the counter decreases the registration performance
    """
    self.setup_logger(logger_context)

    events_ids = Event.objects.filter(
        start_time__gte=timezone.now(), merge_time__gte=timezone.now()
    ).values_list("id", flat=True)

    for event_id in events_ids:
        with transaction.atomic():
            locked_event = Event.objects.select_for_update().get(pk=event_id)
            for pool in locked_event.pools.all():
                registration_count = pool.registrations.count()
                if pool.counter != registration_count:
                    log.critical("pool_counter_not_equal_registration_count", pool=pool)
                    raise PoolCounterNotEqualToRegistrationCount(
                        pool, registration_count, locked_event
                    )
