from itertools import chain

from rest_framework import decorators, viewsets
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin

from .models import Page
from .serializers import PageDetailSerializer, PageListSerializer


class PageViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Page.objects.all()
    order_by = 'created_at'
    lookup_field = 'slug'

    @decorators.detail_route(methods=['GET'])
    def tree(self, request, *args, **kwargs):
        page = self.get_object()
        siblings = page.get_siblings()
        children = page.get_children()
        parent = page.parent

        result = chain(
            PageListSerializer(children, many=True).data,
            PageListSerializer(siblings, many=True).data,
            PageDetailSerializer([page], many=True).data
        )

        if parent:
            result = chain(
                result,
                PageListSerializer([parent], many=True).data
            )
        return Response(result)

    def get_serializer_class(self):
        if self.action == 'list':
            return PageListSerializer

        return PageDetailSerializer
