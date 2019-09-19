from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from lego.apps.emojis.models import Category, Emoji
from lego.apps.files.fields import ImageField
from lego.utils.serializers import BasisModelSerializer


class CategorySerializer(BasisModelSerializer):
    class Meta:
        model = Category
        fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "name",
            "unicode_string",
        )


class EmojiSerializer(BasisModelSerializer):
    # TODO: consider category = CategorySerializer()
    image = ImageField(required=False, options={"height": 24})

    class Meta:
        model = Emoji
        fields = (
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "short_code",
            "keywords",
            "unicode_string",
            "fitzpatrick_scale",
            "category",
            "image",
        )
