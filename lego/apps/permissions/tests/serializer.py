from rest_framework import serializers

from lego.apps.permissions.tests.models import TestModel


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = '__all__'
