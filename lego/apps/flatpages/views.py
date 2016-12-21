from rest_framework import viewsets

from lego.apps.permissions.views import PermissionsMixin

from .models import Page
from .serializers import PageSerializer


class PageViewSet(PermissionsMixin, viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    order_by = 'created_at'
