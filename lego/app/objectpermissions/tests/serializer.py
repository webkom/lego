# -*- coding: utf8 -*-
from rest_framework import serializers

from lego.app.objectpermissions.tests.model import TestModel


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
