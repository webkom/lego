from rest_framework.exceptions import APIException


class NoAvailablePools(APIException):
    status_code = 400
    default_detail = 'No available pools.'


class NoSuchPool(APIException):
    status_code = 400
    default_detail = 'No such pool for this event.'


class RegistrationException(APIException):
    status_code = 403


class PaymentExists(APIException):
    status_code = 403
    default_detail = 'Payment already exist.'


class RegistrationsExistsInPool(APIException):
    status_code = 409
    default_detail = 'Registrations exists within this pool'
