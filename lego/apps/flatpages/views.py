from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from lego.apps.permissions.views import PermissionsMixin

from .models import Page
from .serializers import PageSerializer


class PageViewSet(PermissionsMixin, viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    order_by = 'created_at'
    lookup_field = 'slug'

    @detail_route(methods=['GET'])
    def hierarchy(self, request, slug=None):
        page = self.queryset.get(slug=slug)
        tree = page.get_family()
        serialized = PageSerializer(tree, many=True)
        return Response(serialized.data)
