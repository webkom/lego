from rest_framework import viewsets

from lego.permissions.filters import ObjectPermissionsFilter

from .models import Page
from .permissions import FlatpagePermissions
from .serializers import PageSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    filter_backends = (ObjectPermissionsFilter,)

    permission_classes = (FlatpagePermissions,)
