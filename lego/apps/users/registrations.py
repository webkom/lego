from django.conf import settings
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner


class Registrations:
    @staticmethod
    def generate_registration_token(email):
        return TimestampSigner().sign(signing.dumps({
            'email': email
        }))

    @staticmethod
    def validate_registration_token(token):
        try:
            return signing.loads(TimestampSigner().unsign(
                token,
                max_age=settings.REGISTRATION_CONFIRMATION_TIMEOUT
            ))['email']
        except (BadSignature, SignatureExpired):
            return None

    @staticmethod
    def generate_student_confirmation_token(student_username, course, member):
        data = signing.dumps({
            'student_username': student_username.lower(),
            'course': course,
            'member': member
        })
        token = TimestampSigner().sign(data)
        return token

    @staticmethod
    def validate_student_confirmation_token(token):
        try:
            return signing.loads(TimestampSigner().unsign(
                token,
                max_age=settings.STUDENT_CONFIRMATION_TIMEOUT
            ))
        except (BadSignature, SignatureExpired):
            return None
