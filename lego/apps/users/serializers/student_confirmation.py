from rest_framework import serializers

from lego.apps.users import constants
from lego.apps.users.models import User


class StudentConfirmationSerializer(serializers.ModelSerializer):
    captcha_response = serializers.CharField(required=True)
    course = serializers.ChoiceField(choices=(
        constants.DATA,
        constants.KOMTEK
    ))
    member = serializers.BooleanField()

    class Meta:
        model = User
        fields = ('student_username', 'course', 'member', 'captcha_response')
