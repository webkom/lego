from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner


def generate_token(user):
    return TimestampSigner(key=settings.ABAID_SECRET_KEY).sign(str(user.pk))


def validate_token(token):
    try:
        user_id = TimestampSigner(key=settings.ABAID_SECRET_KEY).unsign(
            token, max_age=settings.ABAID_QR_TOKEN_TIMEOUT
        )
        return int(user_id)
    except (BadSignature, SignatureExpired, ValueError):
        return None
