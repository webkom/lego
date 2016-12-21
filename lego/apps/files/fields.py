from rest_framework import serializers

from .models import File
from .storage import storage


class FileField(serializers.PrimaryKeyRelatedField):

    queryset = File.objects.all()

    def __init__(self, **kwargs):
        self.pk_field = 'key'
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return True

    def to_representation(self, value):
        return storage.generate_signed_url(File.bucket, value.pk)
