from rest_framework import serializers

from lego.apps.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    captcha_response = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'captcha_response')
