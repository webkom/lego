from rest_framework import serializers

from lego.apps.users import constants
from lego.apps.users.models import User
from lego.apps.users.validators import student_username_validator


class StudentConfirmationSerializer(serializers.Serializer):
    student_username = serializers.CharField(
        max_length=30,
        help_text='30 characters or fewer. Letters, digits and ./-/_ only.',
        validators=[student_username_validator]
    )
    captcha_response = serializers.CharField()
    course = serializers.ChoiceField(choices=(
        constants.DATA,
        constants.KOMTEK
    ))
    member = serializers.BooleanField()

    def validate_student_username(self, value):
        if User.objects.filter(student_username=value.lower()).exists():
            raise serializers.ValidationError("A user has already verified that student username.")
        return value.lower()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
