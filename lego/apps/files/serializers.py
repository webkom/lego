from rest_framework import serializers

from .models import File
from .validators import KEY_REGEX


class FileUploadSerializer(serializers.Serializer):
    key = serializers.RegexField(regex=KEY_REGEX)


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('key', )
