from rest_framework import serializers


class UserDeleteSerializer(serializers.Serializer):

    password = serializers.CharField(style={"input_type": "password"})
    default_error_messages = {
        "invalid_password": "Invalid password.",
    }

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(self.error_messages["invalid_password"])
        return value
