from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import File
from .storage import storage


class FileField(serializers.PrimaryKeyRelatedField):

    default_error_messages = {
        'required': 'This field is required.',
        'does_not_exist': 'Invalid pk "{pk_value}" - object does not exist.',
        'incorrect_type': 'Incorrect type. Expected pk value, received {data_type}.',
        'incorrect_token': 'Incorrect file token, you cannot access this file.'
    }
    allowed_types = None

    def __init__(self, allowed_types=None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_types = allowed_types

    def get_queryset(self):
        if not self.allowed_types:
            return File.objects.all()
        return File.objects.filter(file_type__in=self.allowed_types)

    def use_pk_only_optimization(self):
        return True

    def to_representation(self, value):
        return storage.generate_signed_url(File.bucket, value.pk)

    def to_internal_value(self, data):
        try:
            key, token = data.split(':')
        except ValueError:
            self.fail('incorrect_token')

        try:
            file = self.get_queryset().get(key=key)

            if file.token != token:
                self.fail('incorrect_token')

            return file
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)
