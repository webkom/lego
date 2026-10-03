from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner


def generate_token(user):
    return TimestampSigner(key=settings.ABAID_SECRET_KEY).sign(
        f"{user.pk}:{user.username}"
    )


def validate_token(token):
    try:
        value = TimestampSigner(key=settings.ABAID_SECRET_KEY).unsign(
            token, max_age=settings.ABAID_QR_TOKEN_TIMEOUT
        )
        return int(value.split(":", 1)[0])
    except (BadSignature, SignatureExpired, ValueError):
        return None
