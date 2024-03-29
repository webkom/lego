from urllib.parse import unquote

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import URLValidator
from rest_framework import serializers

from lego.apps.files.constants import IMAGE
from lego.apps.files.thumbor import generate_url

from .models import File
from .storage import storage

url_validator = URLValidator()


class FileField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        "required": "This field is required.",
        "does_not_exist": 'Invalid pk "{pk_value}" - object does not exist.',
        "incorrect_type": "Incorrect type. Expected pk value, received {data_type}.",
        "incorrect_token": "Incorrect file token, you cannot access this file.",
    }
    allowed_types = None

    def __init__(self, allowed_types=None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_types = allowed_types
        self.access_granted = False

    def get_queryset(self):
        if not self.allowed_types:
            return File.objects.all()
        return File.objects.filter(file_type__in=self.allowed_types)

    def use_pk_only_optimization(self):
        return True

    def to_representation(self, value):
        return storage.generate_signed_url(File.bucket, value.pk)

    def run_validation(self, data=None):
        if data is None:
            data = ""

        # Remove urls, url is not valid as a file
        self.access_granted = False
        try:
            url_validator(str(data))
        except ValidationError:
            pass
        else:
            data = getattr(self.parent.instance, f"{self.source}_id")
            self.access_granted = True

        return super().run_validation(data)

    def to_internal_value(self, data):
        if self.access_granted:
            key, token = data, None
        else:
            try:
                key, token = data.split(":")
            except ValueError:
                self.fail("incorrect_token")

        try:
            file = self.get_queryset().get(key=key)

            if file.token != token and not self.access_granted:
                self.fail("incorrect_token")

            return file
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)


class ImageField(FileField):
    """
    Load images with thumbor and on demand resizing.
    Pass a options dict to the constructor to control thumbor.
    """

    options = {}

    def __init__(self, options=None, **kwargs):
        kwargs["allowed_types"] = [IMAGE]
        super().__init__(**kwargs)

        if options:
            self.options = options

    def to_representation(self, value):
        return generate_url(unquote(value.pk), **self.options)
