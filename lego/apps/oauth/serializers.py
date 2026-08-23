from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from oauth2_provider.models import AccessToken

from lego.apps.users.fields import PublicUserField

from .fields import ApplicationField, ProtectedTokenField
from .models import APIApplication


class ApplicationSerializer(serializers.ModelSerializer):
    user = PublicUserField(read_only=True)

    class Meta:
        model = APIApplication
        fields = [
            "id",
            "name",
            "description",
            "redirect_uris",
            "client_id",
            "client_secret",
            "user",
        ]
        read_only_fields = ["client_id", "client_secret", "user"]

    def save(self, **kwargs):
        """
        Save application with secure parameters.
        """
        if (
            isinstance(self.instance, APIApplication)
            and self.instance.authorization_grant_type
            == APIApplication.GRANT_CLIENT_CREDENTIALS
        ):
            # The forced fields below would silently downgrade a machine
            # application; those are managed from the shell only.
            raise PermissionDenied(
                "Maskinapplikasjoner (client_credentials) kan ikke endres her."
            )
        request = self.context["request"]
        kwargs["user"] = request.user
        kwargs.update(
            {
                "skip_authorization": False,
                "client_type": APIApplication.CLIENT_PUBLIC,
                "authorization_grant_type": APIApplication.GRANT_AUTHORIZATION_CODE,
            }
        )
        return super().save(**kwargs)


class AccessTokenSerializer(serializers.ModelSerializer):
    application = ApplicationField(read_only=True)
    token = ProtectedTokenField(read_only=True)

    class Meta:
        model = AccessToken
        fields = ["id", "user", "token", "application", "expires", "scopes"]
