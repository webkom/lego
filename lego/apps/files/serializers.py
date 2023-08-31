from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from lego.apps.files.models import File

from .validators import KEY_REGEX


class FileUploadSerializer(serializers.Serializer):
    key = serializers.RegexField(regex=KEY_REGEX)
    public = serializers.BooleanField(required=True)


class FileSaveForUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        save_for_use = serializers.BooleanField(required=True)

        fields = (
            "token",
            "save_for_use",
        )

    def validate(self, data):
        if self.instance.token != data["token"]:
            raise PermissionDenied()
        if "save_for_use" not in data:
            raise ValidationError()
        return data
