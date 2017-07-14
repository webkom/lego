from rest_framework import serializers

from lego.apps.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    captcha_response = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'captcha_response')


class RegistrationConfirmationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'gender',
            'email',
            'password'
        )
