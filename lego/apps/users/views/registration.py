from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from structlog import get_logger

from lego.apps.users.models import User
from lego.apps.users.serializers.registration import RegistrationSerializer
from lego.utils.functions import verify_captcha
from lego.utils.tasks import send_email

log = get_logger()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny, )

    """
    Validates a registration token.

    The request errors out if the token has expired or is invalid.
    Request URL: GET /api/v1/users/registration/?token=<token>
    """
    def get(self, request, pk=None, format=None):
        if not request.GET.get('token', False):
            # Raise a validation error if the token is not set.
            raise ValidationError(detail='Registration token is required.')
        # Validating the token returns the username of the user that registered.
        token_username = User.validate_registration_token(request.GET.get('token', False))
        if token_username is None:
            # Raise error if the token has expired or is invalid.
            raise ValidationError(detail='Token expired or invalid.')
        # Return an object with the username.
        return Response({'username': token_username}, status=status.HTTP_200_OK)

    """
    Attempts to create a registration token and email it to the user.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # User does not exist and the username is valid, continue the registration.
        if not verify_captcha(serializer.validated_data.get('captcha_response', None)):
            # The captcha response from the user is invalid, return a validation error.
            raise ValidationError(detail='Bad captcha')

        # Get the username from the serializer.
        username = serializer.data.get('username')

        # Generate a token for the registration confirmation
        token = User.generate_registration_token(username)

        # Send the registration confirmation email.
        send_email(
            to_email=f'{username}@stud.ntnu.no',
            context={
                "username": username,
                "token": token,
                "email_title": 'Velkommen til Abakus.no'
            },
            subject='Velkommen til Abakus.no',
            plain_template='users/email/registration.html',
            html_template='users/email/registration.txt',
            from_email=None
        )

        # Return a response that the registration was successful.
        return Response(status=status.HTTP_202_ACCEPTED)
