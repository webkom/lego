from rest_framework import status
from rest_framework.exceptions import APIException


class APIReactionExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Reaction already exists."


class APITooManyReactions(APIException):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = "Too many reactions for this target"


class ReactionExists(ValueError):
    pass


class TooManyReactions(ValueError):
    pass
