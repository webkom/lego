from django.conf import settings
from django.core import signing
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired


class PasswordReset:

    @classmethod
    def generate_reset_token(cls, email):
        return TimestampSigner().sign(signing.dumps({
            'email': email
        }))

    @staticmethod
    def validate_reset_token(token):
        try:
            return signing.loads(TimestampSigner().unsign(
                token,
                max_age=settings.PASSWORD_RESET_TIMEOUT
            ))['email']
        except (BadSignature, SignatureExpired):
            return None
