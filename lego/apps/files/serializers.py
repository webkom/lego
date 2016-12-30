from rest_framework import serializers

from .validators import KEY_REGEX


class FileUploadSerializer(serializers.Serializer):
    key = serializers.RegexField(regex=KEY_REGEX)
