COMPANY_PRESENTATION = "company_presentation"
LUNCH_PRESENTATION = "lunch_presentation"
ALTERNATIVE_PRESENTATION = "alternative_presentation"
COURSE = "course"
KID_EVENT = "kid_event"
PARTY = "party"
SOCIAL = "social"
OTHER = "other"
EVENT = "event"

EVENT_TYPES = (
    (COMPANY_PRESENTATION, COMPANY_PRESENTATION),
    (LUNCH_PRESENTATION, LUNCH_PRESENTATION),
    (ALTERNATIVE_PRESENTATION, ALTERNATIVE_PRESENTATION),
    (COURSE, COURSE),
    (KID_EVENT, KID_EVENT),
    (PARTY, PARTY),
    (SOCIAL, SOCIAL),
    (OTHER, OTHER),
    (EVENT, EVENT),
)

"""
Events marked as NORMAL are events that can have infinite pools.
This even status type should be used for most events.
"""
NORMAL = "NORMAL"
"""
Events marked as INFINITE should have exactly 1 pool, with capacity set to 0.
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

UNKNOWN = "UNKNOWN"
PRESENT = "PRESENT"
NOT_PRESENT = "NOT_PRESENT"

PRESENCE_CHOICES = ((UNKNOWN, UNKNOWN), (PRESENT, PRESENT), (NOT_PRESENT, NOT_PRESENT))

PHOTO_CONSENT = "PHOTO_CONSENT"
PHOTO_NOT_CONSENT = "PHOTO_NOT_CONSENT"

PHOTO_CONSENT_CHOICES = (
    (UNKNOWN, UNKNOWN),
    (PHOTO_CONSENT, PHOTO_CONSENT),
    (PHOTO_NOT_CONSENT, PHOTO_NOT_CONSENT),
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

STRIPE_EVENT_INTENT_SUCCESS = "payment_intent.success"
STRIPE_EVENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"
STRIPE_EVENT_CHARGE_REFUNDED = "charge.refunded"

SOCKET_INITIATE_PAYMENT_SUCCESS = "Event.SOCKET_INITIATE_PAYMENT.SUCCESS"
SOCKET_INITIATE_PAYMENT_FAILURE = "Event.SOCKET_INITIATE_PAYMENT.FAILURE"

SOCKET_PAYMENT_SUCCESS = "Event.SOCKET_PAYMENT.SUCCESS"
SOCKET_PAYMENT_FAILURE = "Event.SOCKET_PAYMENT.FAILURE"

SOCKET_REGISTRATION_SUCCESS = "Event.SOCKET_REGISTRATION.SUCCESS"
SOCKET_REGISTRATION_FAILURE = "Event.SOCKET_REGISTRATION.FAILURE"
SOCKET_UNREGISTRATION_SUCCESS = "Event.SOCKET_UNREGISTRATION.SUCCESS"
SOCKET_UNREGISTRATION_FAILURE = "Event.SOCKET_UNREGISTRATION.FAILURE"

DAYS_BETWEEN_NOTIFY = 1

# Event registration closes a certain amount of hours before the start time
REGISTRATION_CLOSE_TIME = 2
