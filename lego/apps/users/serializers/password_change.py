from django.contrib.auth import password_validation
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):

    password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(style={'input_type': 'password'})
    retype_new_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': 'Invalid password.',
        'password_mismatch': 'The two password fields didn\'t match.',
    }

    def validate_password(self, value):
        user = self.context['request'].user
        if user.has_usable_password() and not user.check_password(value):
            raise serializers.ValidationError(self.error_messages['invalid_password'])
        return value

    def validate_new_password(self, password):
        if password:
            password_validation.validate_password(password)
        return password

    def validate(self, attrs):
        if attrs['new_password'] != attrs['retype_new_password']:
            raise serializers.ValidationError(self.error_messages['password_mismatch'])
        return attrs
