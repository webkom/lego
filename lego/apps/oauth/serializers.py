from oauth2_provider.models import AccessToken
from rest_framework import serializers

from .fields import ApplicationField, ProtectedTokenField
from .models import APIApplication


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = APIApplication
        fields = [
            'id', 'name', 'description', 'redirect_uris', 'client_id', 'client_secret',
        ]
        read_only_fields = ['client_id', 'client_secret', 'user']

    def save(self, **kwargs):
        """
        Save application with secure parameters.

        """
        request = self.context['request']
        kwargs['user'] = request.user
        kwargs.update({
            'skip_authorization': False,
            'client_type': APIApplication.CLIENT_PUBLIC,
            'authorization_grant_type': APIApplication.GRANT_AUTHORIZATION_CODE,
        })
        super().save(**kwargs)


class AccessTokenSerializer(serializers.ModelSerializer):
    application = ApplicationField(read_only=True)
    token = ProtectedTokenField(read_only=True)

    class Meta:
        model = AccessToken
        fields = ['id', 'user', 'token', 'application', 'expires', 'scopes']
