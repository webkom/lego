from django.contrib.auth import password_validation
from rest_framework import exceptions, serializers

from lego.apps.users.models import User
from lego.utils.functions import verify_captcha


class RegistrationSerializer(serializers.ModelSerializer):
    captcha_response = serializers.CharField(required=True)

    def validate_captcha_response(self, captcha_response):
        if not verify_captcha(captcha_response):
            raise exceptions.ValidationError('invalid_captcha')
        return captcha_response

    class Meta:
        model = User
        fields = ('email', 'captcha_response')


class RegistrationConfirmationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(required=True, write_only=True)

    def validate_username(self, username):
        username_exists = User.objects.filter(username__iexact=username).exists()
        if username_exists:
            raise exceptions.ValidationError('Username exists')
        return username

    def validate_password(self, password):
        password_validation.validate_password(password)
        return password

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'gender',
            'password',
            'allergies'
        )
