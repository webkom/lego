from rest_framework import serializers

from lego.permissions.tests.models import TestModel


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
