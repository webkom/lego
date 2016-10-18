from rest_framework.exceptions import APIException


class NoAvailablePools(APIException):
    status_code = 400
    default_detail = 'No available pools.'


class NoSuchPool(APIException):
    status_code = 403
    default_detail = 'No such pool for this event'
