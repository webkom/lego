from rest_framework import serializers

from lego.apps.users import constants
from lego.apps.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    captcha_response = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'captcha_response')


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


class RegistrationConfirmationAdditionalSerializer(serializers.Serializer):
    course = serializers.ChoiceField(choices=(
        constants.DATA,
        constants.KOMTEK
    ))
    member = serializers.BooleanField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
