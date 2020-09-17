from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin

from .models import Page
from .serializers import (
    PageDetailAuthSerializer,
    PageDetailSerializer,
    PageListSerializer,
)


class PageViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Page.objects.all()
    order_by = "created_at"
    lookup_field = "slug"
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "list":
            return PageListSerializer
        if self.request and self.request.user.is_authenticated:
            return PageDetailAuthSerializer
        return PageDetailSerializer
