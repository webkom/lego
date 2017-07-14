from rest_framework.exceptions import APIException


class APINoSuchPool(APIException):
    status_code = 400
    default_detail = 'No such pool for this event.'


class APIPaymentExists(APIException):
    status_code = 403
    default_detail = 'Payment already exist.'


class APIRegistrationsExistsInPool(APIException):
    status_code = 409
    default_detail = 'Registrations exists within this pool'


class NoSuchPool(ValueError):
    pass


class EventHasStarted(ValueError):
    pass


class RegistrationsExistInPool(ValueError):
    pass
