from django.db.models import Q
from rest_framework import exceptions, serializers

from lego.apps.users.constants import GROUP_BOARD, GROUP_COMMITTEE
from lego.apps.users.models import AbakusGroup
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.functions import verify_captcha


class ContactFormSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=80)
    message = serializers.CharField()
    captcha_response = serializers.CharField()
    recipient_group = PrimaryKeyRelatedFieldNoPKOpt(
        allow_null=True,
        queryset=AbakusGroup.objects.all().filter(
            Q(type=GROUP_COMMITTEE) | Q(type=GROUP_BOARD)
        ),
    )

    def validate_captcha_response(self, captcha_response):
        if not verify_captcha(captcha_response):
            raise exceptions.ValidationError("invalid_captcha")
        return captcha_response
