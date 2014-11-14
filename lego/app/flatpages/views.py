# -*- coding: utf8 -*-
from lego.app.objectpermissions.filters import ObjectPermissionsFilter
from lego.app.objectpermissions.permissions import ObjectPermissions
from lego.users.permissions import AbakusModelPermissions
from rest_framework import viewsets, serializers, permissions

from .models import Page


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = UserSerializer
    filter_backends = ObjectPermissionsFilter,

    permission_classes = [
        permissions.DjangoModelPermissionsOrAnonReadOnly,
        AbakusModelPermissions,
        ObjectPermissions
    ]
