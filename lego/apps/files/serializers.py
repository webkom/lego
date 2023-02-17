from rest_framework import serializers

from lego.apps.files.fields import ImageField
from lego.apps.files.models import File

from .validators import KEY_REGEX


class FileUploadSerializer(serializers.Serializer):
    key = serializers.RegexField(regex=KEY_REGEX)
    public = serializers.BooleanField(required=True)


class ImageGalleryCoverSerializer(serializers.ModelSerializer):

    file = ImageField(
        source="self", required=False, options={"height": 700, "smart": True}
    )

    thumbnail = ImageField(
        source="self",
        read_only=True,
        options={"height": 300, "width": 300, "smart": True},
    )

    class Meta:
        model = File
        fields = (
            "thumbnail",
            "id",
            "key",
        )
