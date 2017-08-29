from django.contrib.auth import password_validation
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from structlog import get_logger

from lego.apps.users.models import User
from lego.apps.users.password_reset import PasswordReset
from lego.apps.users.serializers.users import DetailedUserSerializer
from lego.utils.tasks import send_email

from lego.apps.users.serializers.password_reset import PasswordResetRequestSerializer, \
    PasswordResetPerformSerializer

log = get_logger()


class PasswordResetRequestViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError({"email": "User with that email does not exist"})
        token = PasswordReset.generate_reset_token(email)
        send_email.delay(
            to_email=email,
            context={
                "token": token,
            },
            subject='Nullstill ditt passord på abakus.no',
            plain_template='users/email/password_reset.html',
            html_template='users/email/password_reset.txt',
            from_email=None
        )

        return Response(status=status.HTTP_202_ACCEPTED)


class PasswordResetPerformViewSet(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = PasswordResetPerformSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.data['token']
        password = serializer.data['password']

        password_validation.validate_password(password)
        email = PasswordReset.validate_reset_token(token)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError({"email": "User with that email does not exist"})

        user.set_password(password)
        user.save()
        return Response(DetailedUserSerializer(user).data, status=status.HTTP_200_OK)
