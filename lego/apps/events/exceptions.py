from rest_framework.exceptions import APIException


class APINoSuchPool(APIException):
    status_code = 400
    default_detail = "No such pool for this event."


class APIPaymentExists(APIException):
    status_code = 403
    default_detail = "Payment already exists."


class APIPaymentDenied(APIException):
    status_code = 403
    default_detail = "The registration is not permitted to pay."


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


class NoPhoneNumber(ValueError):
    pass


class NotRegisteredPhotoConsents(ValueError):
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
    MAX_POOLS_IN_MESSAGE = 10

    def __init__(self, mismatches):
        """
        :param mismatches: list of (pool_id, event_id, counter, registration_count)
        """
        # Celery and pickle rebuild exceptions as cls(*args), and args hold the message.
        if isinstance(mismatches, str):
            self.mismatches = []
            super().__init__(mismatches)
            return

        self.mismatches = mismatches
        details = [
            f"Pool {pool_id} for event {event_id} was supposed to have "
            f"{counter} registrations, but has {registration_count}"
            for pool_id, event_id, counter, registration_count in mismatches
        ]

        if len(details) == 1:
            super().__init__(f"{details[0]}!")
            return

        listed = details[: self.MAX_POOLS_IN_MESSAGE]
        remaining = len(details) - len(listed)
        message = (
            f"{len(details)} pools have a counter that does not match their "
            f"registration count: " + "; ".join(listed)
        )
        if remaining:
            message += f"; and {remaining} more"
        super().__init__(message)


class WebhookDidNotFindRegistration(ValueError):
    def __init__(self, event_id, metadata):
        message = (
            f"Stripe webhook with ID: {event_id} for event {metadata['EVENT_ID']} tried "
            f"getting registration for user {metadata['USER']}, but did not find any!"
        )
        super().__init__(message)
