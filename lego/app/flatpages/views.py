# -*- coding: utf8 -*-
from rest_framework import viewsets, serializers, permissions

from lego.api.filters import RequireAuthFilterBackend
from .models import Page


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = UserSerializer
    filter_backends = RequireAuthFilterBackend,

    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
