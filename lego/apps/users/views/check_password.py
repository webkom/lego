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


class CheckPasswordViewSet(viewsets.GenericViewSet):

    serializer_class = PasswordResetPerformSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.check_password(serializer.validated_data["new_password"])
        self.request.user.save()
token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        password_validation.validate_password(password)
        email = PasswordReset.validate_reset_token(token)
        user = User.objects.get(username=username)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValidationError({"password": "Wrong password"})

        user.set_password(password)
        user.save()
        return Response(DetailedUserSerializer(user).data, status=status.HTTP_200_OK)
