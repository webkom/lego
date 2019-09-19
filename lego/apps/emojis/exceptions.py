from rest_framework.exceptions import APIException


class ApiNoSuchEmoji(APIException):
    status_code = 400
    default_detail = "No such emoji exists."


class APIEmojiExists(APIException):
    status_code = 400
    default_detail = "A emoji with this short code already exists."


class APIEmojisExistsInCategory(APIException):
    status_code = 409
    default_detail = "Emojis exists within this category."


class NoSuchEmoji(ValueError):
    pass


class EmojiExists(ValueError):
    pass


class EmojisExistsInCategory(ValueError):
    pass
