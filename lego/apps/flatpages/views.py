from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin

from .models import Page
from .serializers import PageDetailSerializer, PageListSerializer


class PageViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Page.objects.all()
    order_by = 'created_at'
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return PageListSerializer

        return PageDetailSerializer
