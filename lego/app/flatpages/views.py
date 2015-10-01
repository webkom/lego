from rest_framework import serializers, viewsets

from lego.app.flatpages.permissions import FlatpagePermissions
from lego.permissions.filters import ObjectPermissionsFilter

from .models import Page


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = UserSerializer
    filter_backends = (ObjectPermissionsFilter,)

    permission_classes = (FlatpagePermissions,)
