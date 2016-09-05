from oauth2_provider.models import AccessToken
from rest_framework import serializers

from .fields import ApplicationField, ProtectedTokenField
from .models import APIApplication


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = APIApplication
        fields = ['id', 'name', 'description', 'user', 'redirect_uris', 'client_type',
                  'authorization_grant_type', 'client_id', 'client_secret', 'skip_authorization']
        read_only_fields = ['client_id', 'client_secret']


class AccessTokenSerializer(serializers.ModelSerializer):
    application = ApplicationField(read_only=True)
    token = ProtectedTokenField(read_only=True)

    class Meta:
        model = AccessToken
        fields = ['id', 'user', 'token', 'application', 'expires', 'scopes']
