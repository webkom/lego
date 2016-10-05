from rest_framework.exceptions import APIException


class NoAvailablePools(APIException):
    status_code = 400
    default_detail = 'No available pools.'


class UserNotAdmin(APIException):
    status_code = 403
    default_detail = 'User does not have admin rights for this event'
