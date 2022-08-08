from django.contrib.auth import password_validation
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from structlog import get_logger

from lego.apps.users.models import User
from lego.apps.users.password_reset import PasswordReset
from lego.apps.users.serializers.password_reset import (
    PasswordResetPerformSerializer,
    PasswordResetRequestSerializer,
)
from lego.apps.users.serializers.users import DetailedUserSerializer
from lego.utils.tasks import send_email

log = get_logger()


class PasswordResetRequestViewSet(viewsets.GenericViewSet):

    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as e:
            raise ValidationError(
                {"email": "User with that email does not exist"}
            ) from e
        token = PasswordReset.generate_reset_token(email)
        send_email.delay(
            to_email=email,
            context={"name": user.full_name, "token": token},
            subject="Nullstill ditt passord på abakus.no",
            plain_template="users/email/reset_password.txt",
            html_template="users/email/reset_password.html",
            from_email=None,
        )

        return Response(status=status.HTTP_202_ACCEPTED)


class PasswordResetPerformViewSet(viewsets.GenericViewSet):

    serializer_class = PasswordResetPerformSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        password_validation.validate_password(password)
        email = PasswordReset.validate_reset_token(token)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as e:
            raise ValidationError(
                {"email": "User with that email does not exist"}
            ) from e

        user.set_password(password)
        user.save()
        return Response(DetailedUserSerializer(user).data, status=status.HTTP_200_OK)
