from django.db import models

COMPANY_PRESENTATION = "company_presentation"
LUNCH_PRESENTATION = "lunch_presentation"
ALTERNATIVE_PRESENTATION = "alternative_presentation"
COURSE = "course"
BREAKFAST_TALK = "breakfast_talk"
NEXUS_EVENT = "nexus_event"
PARTY = "party"
SOCIAL = "social"
GALA = "gala"
OTHER = "other"
EVENT = "event"
INTEREST_EVENT = "interest_event"

EVENT_TYPES = (
    (COMPANY_PRESENTATION, COMPANY_PRESENTATION),
    (LUNCH_PRESENTATION, LUNCH_PRESENTATION),
    (ALTERNATIVE_PRESENTATION, ALTERNATIVE_PRESENTATION),
    (COURSE, COURSE),
    (BREAKFAST_TALK, BREAKFAST_TALK),
    (NEXUS_EVENT, NEXUS_EVENT),
    (PARTY, PARTY),
    (SOCIAL, SOCIAL),
    (GALA, GALA),
    (OTHER, OTHER),
    (EVENT, EVENT),
    (INTEREST_EVENT, INTEREST_EVENT),
)

EVENT_TYPE_TRANSLATIONS = {
    COMPANY_PRESENTATION: "Bedriftspresentasjon",
    LUNCH_PRESENTATION: "Lunchpresentasjon",
    ALTERNATIVE_PRESENTATION: "Alternativ presentasjon",
    COURSE: "Kurs",
    BREAKFAST_TALK: "Frokostforedrag",
    NEXUS_EVENT: "NEXUS-arrangement",
    PARTY: "Fest",
    SOCIAL: "Sosialt",
    GALA: "Galla",
    OTHER: "Annet",
    EVENT: "Arrangement",
    INTEREST_EVENT: "Interesse arrangement",
}

"""
Events marked as NORMAL are events that can have infinite pools.
This even status type should be used for most events.
"""
NORMAL = "NORMAL"
"""
Events marked as INFINITE should have exactly 1 pool. Capacity 0 (the
default) means unlimited; a capacity can be set to limit the number of spots,
with the waiting list handling the overflow.
A user _should_ be able to sign up to the event.
There are no permissions (except Abakom).
This even status type should be used for events such as Abakom Works, etc.
"""
INFINITE = "INFINITE"
"""
Events marked as OPEN should have 0 pools, like TBA. Location is required.
A user should _not_ be able to sign up to the event.
There are no permissions (except Abakom).
This even status type should be used for events hosted by LaBamba, etc.
"""
OPEN = "OPEN"
"""
Events marked as TBA should have 0 pools, location will be set to TBA.
A user should _not_ be able to sign up to the event.
There are no permissions (except Abakom).
TBA should be used for events that need additional information, as a placeholder.
This is the default even status type.
"""
TBA = "TBA"
EVENT_STATUS_TYPES = ((NORMAL, NORMAL), (INFINITE, INFINITE), (OPEN, OPEN), (TBA, TBA))

"""
The complete contract for interest events, enforced by
EventCreateAndUpdateSerializer: creators (interest group leaders) control the
CREATOR_FIELDS, the FORCED_FIELDS always get these values, and any other
event field is dropped from the payload. New event fields are therefore
locked for interest events until explicitly added here.
"""
INTEREST_EVENT_CREATOR_FIELDS = frozenset(
    {
        "id",
        "event_type",
        "title",
        "description",
        "text",
        "start_time",
        "end_time",
        "location",
        "mazemap_poi",
        "responsible_group",
        "pools",
    }
)
INTEREST_EVENT_FORCED_FIELDS: dict = {
    "event_status_type": INFINITE,
    "use_captcha": False,
    "heed_penalties": False,
    "feedback_required": False,
    "feedback_description": "",
    "is_priced": False,
    "pinned": False,
    "registration_deadline_hours": 0,
    "unregistration_deadline_hours": 0,
    "can_view_groups": (),
    "require_auth": False,
    "company": None,
    "show_company_description": False,
}


class PRESENCE_CHOICES(models.TextChoices):
    UNKNOWN = "UNKNOWN"
    PRESENT = "PRESENT"
    LATE = "LATE"
    NOT_PRESENT = "NOT_PRESENT"


UNKNOWN = "UNKNOWN"
LEGACY_PHOTO_CONSENT = "PHOTO_CONSENT"
LEGACY_PHOTO_NOT_CONSENT = "PHOTO_NOT_CONSENT"

LEGACY_PHOTO_CONSENT_CHOICES = (
    (UNKNOWN, UNKNOWN),
    (LEGACY_PHOTO_CONSENT, LEGACY_PHOTO_CONSENT),
    (LEGACY_PHOTO_NOT_CONSENT, LEGACY_PHOTO_NOT_CONSENT),
)

PENDING_REGISTER = "PENDING_REGISTER"
SUCCESS_REGISTER = "SUCCESS_REGISTER"
FAILURE_REGISTER = "FAILURE_REGISTER"

PENDING_UNREGISTER = "PENDING_UNREGISTER"
SUCCESS_UNREGISTER = "SUCCESS_UNREGISTER"
FAILURE_UNREGISTER = "FAILURE_UNREGISTER"

STATUSES = (
    (PENDING_REGISTER, PENDING_REGISTER),
    (SUCCESS_REGISTER, SUCCESS_REGISTER),
    (FAILURE_REGISTER, FAILURE_REGISTER),
    (PENDING_UNREGISTER, PENDING_UNREGISTER),
    (SUCCESS_UNREGISTER, SUCCESS_UNREGISTER),
    (FAILURE_UNREGISTER, FAILURE_UNREGISTER),
)

PAYMENT_PENDING = "pending"
PAYMENT_SUCCESS = "succeeded"
PAYMENT_FAILURE = "failed"
PAYMENT_MANUAL = "manual"
PAYMENT_CANCELED = "canceled"

PAYMENT_STATUS_CHOICES = (
    (PAYMENT_MANUAL, PAYMENT_MANUAL),
    (PAYMENT_SUCCESS, PAYMENT_SUCCESS),
    (PAYMENT_FAILURE, PAYMENT_FAILURE),
    (PAYMENT_PENDING, PAYMENT_PENDING),
)

STRIPE_EVENT_INTENT_SUCCESS = "payment_intent.succeeded"
STRIPE_EVENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"
STRIPE_EVENT_INTENT_PAYMENT_CANCELED = "payment_intent.canceled"
STRIPE_EVENT_CHARGE_REFUNDED = "charge.refunded"

# See https://stripe.com/docs/api/payment_intents/object#payment_intent_object-status
STRIPE_INTENT_REQUIRES_PAYMENT = "requires_payment_method"
STRIPE_INTENT_REQUIRES_CONFIRMATION = "requires_confirmaion"
STRIPE_INTENT_SUCCEEDED = "succeeded"
STRIPE_INTENT_PROCESSING = "processing"
STRIPE_INTENT_CANCELED = "canceled"
STRIPE_INTENT_REQUIRES_ACTION = "requires_action"
STRIPE_INTENT_REQUIRES_CAPTURE = "requires_capture"


SOCKET_INITIATE_PAYMENT_SUCCESS = "Event.SOCKET_INITIATE_PAYMENT.SUCCESS"
SOCKET_INITIATE_PAYMENT_FAILURE = "Event.SOCKET_INITIATE_PAYMENT.FAILURE"

SOCKET_PAYMENT_SUCCESS = "Event.SOCKET_PAYMENT.SUCCESS"
SOCKET_PAYMENT_FAILURE = "Event.SOCKET_PAYMENT.FAILURE"

SOCKET_REGISTRATION_SUCCESS = "Event.SOCKET_REGISTRATION.SUCCESS"
SOCKET_REGISTRATION_FAILURE = "Event.SOCKET_REGISTRATION.FAILURE"
SOCKET_UNREGISTRATION_SUCCESS = "Event.SOCKET_UNREGISTRATION.SUCCESS"
SOCKET_UNREGISTRATION_FAILURE = "Event.SOCKET_UNREGISTRATION.FAILURE"

DAYS_BETWEEN_NOTIFY = 1

# Event registration and unregistration closes a certain amount of hours before the start time
REGISTRATION_CLOSE_TIME = 2
UNREGISTRATION_CLOSE_TIME = 2
