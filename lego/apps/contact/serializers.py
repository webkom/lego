from rest_framework import exceptions, serializers

from lego.utils.functions import verify_captcha
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer


class ContactFormSerializer(serializers.Serializer):

    title = serializers.CharField(max_length=80)
    message = serializers.CharField()
    anonymous = serializers.BooleanField()
    captcha_response = serializers.CharField()
    recipient_group = PublicAbakusGroupSerializer()


    def validate_captcha_response(self, captcha_response):
        if not verify_captcha(captcha_response):
            raise exceptions.ValidationError("invalid_captcha")
        return captcha_response

    def validate_anonymous(self, anonymous):
        if not self.context["request"].user.is_authenticated and not anonymous:
            raise exceptions.ValidationError("anonymous_required_without_auth")
        return anonymous

    def validate_recipient_group(self, recipient_group):
        if not recipient_group.is_committee():
            raise exceptions.ValidationError("group_not_committee")
        return recipient_group