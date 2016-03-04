from rest_framework.exceptions import APIException


class NoAvailablePools(APIException):
    status_code = 400
    default_detail = 'No available pools.'
