# -*- coding: utf8 -*-
from rest_framework import viewsets, serializers

from lego.permissions.filters import ObjectPermissionsFilter
from lego.permissions.object_permissions import ObjectPermissions
from lego.permissions.model_permissions import PostModelPermissions

from .models import Page


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = UserSerializer
    filter_backends = (ObjectPermissionsFilter,)

    permission_classes = (PostModelPermissions, ObjectPermissions)
