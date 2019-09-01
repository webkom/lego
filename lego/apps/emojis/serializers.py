from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from lego.apps.emojis.models import Emoji
from lego.utils.serializers import BasisModelSerializer


class EmojiSerializer(BasisModelSerializer):
    class Meta:
        model = Emoji
        fields = ("id", "keywords", "unicode_string", "fitzpatrick_scale", "category")
