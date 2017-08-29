from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from structlog import get_logger

from lego.apps.users.models import User
from lego.apps.users.registrations import Registrations
from lego.apps.users.serializers.registration import RegistrationSerializer
from lego.utils.tasks import send_email

log = get_logger()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny, )

    def list(self, request):
        """
        Validates a registration token.

        The request errors out if the token has expired or is invalid.
        Request URL: GET /api/v1/users/registration/?token=<token>
        """
        if not request.GET.get('token', False):
            raise ValidationError(detail='Registration token is required.')
        token_email = User.validate_registration_token(request.GET.get('token', False))
        if token_email is None:
            raise ValidationError(detail='Token expired or invalid.')
        return Response({'email': token_email}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Attempts to create a registration token and email it to the user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        token = User.generate_registration_token(email)

        send_email.delay(
            to_email=email,
            context={
                "token": token,
            },
            subject='Velkommen til Abakus.no',
            plain_template='users/email/registration.html',
            html_template='users/email/registration.txt',
            from_email=None
        )

        return Response(status=status.HTTP_202_ACCEPTED)
