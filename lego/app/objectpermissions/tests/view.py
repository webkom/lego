# -*- coding: utf8 -*-
from lego.app.objectpermissions.filters import ObjectPermissionsFilter
from rest_framework import viewsets

from lego.app.objectpermissions.permissions import ObjectPermissions
from lego.app.objectpermissions.tests.model import TestModel
from lego.app.objectpermissions.tests.serializer import TestSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestSerializer
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (ObjectPermissions,)
