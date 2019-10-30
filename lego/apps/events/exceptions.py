from rest_framework.exceptions import APIException


class APINoSuchPool(APIException):
    status_code = 400
    default_detail = "No such pool for this event."


class APIPaymentExists(APIException):
    status_code = 403
    default_detail = "Payment already exist."


class APIEventNotPriced(APIException):
    status_code = 400
    default_detail = "Event is not priced"


class APIEventNotFound(APIException):
    status_code = 400
    default_detail = "No such event"


class APINoSuchRegistration(APIException):
    status_code = 400
    default_detail = "No such registration exists for this event."


class APIRegistrationExists(APIException):
    status_code = 400
    default_detail = "A registration for this user already exists."


class APIRegistrationsExistsInPool(APIException):
    status_code = 409
    default_detail = "Registrations exists within this pool."


class NoSuchPool(ValueError):
    pass


class EventHasClosed(ValueError):
    pass


class UnansweredSurveyException(ValueError):
    pass


class NoSuchRegistration(ValueError):
    pass


class RegistrationExists(ValueError):
    pass


class RegistrationsExistInPool(ValueError):
    pass


class EventNotReady(ValueError):
    pass


class PoolCounterNotEqualToRegistrationCount(ValueError):
    def __init__(self, pool, registration_count, event):
        message = (
            f"Pool {pool.id} for event {event.id} was supposed to have "
            f"{pool.counter} registrations, but has {registration_count}!"
        )
        super().__init__(message)


class WebhookDidNotFindRegistration(ValueError):
    def __init__(self, event_id, metadata):
        message = (
            f'Stripe webhook with ID: {event_id} for event {metadata["EVENT_ID"]} tried '
            f'getting registration for user {metadata["USER"]}, but did not find any!'
        )
        super().__init__(message)
