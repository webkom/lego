from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from lego.apps.users.models import User
from lego.apps.users.serializers.registration import RegistrationSerializer


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
        if request.data['username']:
            # Lowercase the username before sending it to the serializer
            request.data['username'] = request.data['username'].lower()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # User does not exist and the username is valid, continue the registration.

        """
        if not verify_captcha(serializer.validated_data.get('captcha_response', None)):
            # The captcha response from the user is invalid, return a validation error.
            raise ValidationError(detail='Bad captcha')
        """

        # Generate a token for the registration confirmation
        # registration_token = User.generate_registration_token(serializer.data.get('username'))

        # TODO: send an email to the user with the token.
        # print('Token:', registration_token)

        return Response(status=status.HTTP_202_ACCEPTED)
