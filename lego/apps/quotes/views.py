from random import choice

from rest_framework import filters, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.quotes.filters import QuoteModelFilter, QuotesFilterSet
from lego.apps.quotes.models import Quote
from lego.apps.quotes.permissions import QuotePermissions
from lego.apps.quotes.serializers import (QuoteCreateAndUpdateSerializer, QuoteDetailSerializer,
                                          QuoteSerializer)


class QuoteViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Quote.objects.all().prefetch_related('tags')
    filter_backends = (filters.DjangoFilterBackend, QuoteModelFilter)
    filter_class = QuotesFilterSet
    permission_classes = (QuotePermissions, )

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return QuoteDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return QuoteCreateAndUpdateSerializer
        return QuoteSerializer

    @detail_route(methods=['PUT'])
    def approve(self, *args, **kwargs):
        instance = self.get_object()
        instance.approve()
        return Response(status=status.HTTP_200_OK)

    @detail_route(methods=['PUT'])
    def unapprove(self, *args, **kwargs):
        instance = self.get_object()
        instance.unapprove()
        return Response(status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def random(self, request):
        queryset = self.get_queryset().filter(approved=True)
        values = queryset.values_list('pk', flat=True)
        if not values:
            return Response(status=status.HTTP_204_NO_CONTENT)

        instance = queryset.get(pk=choice(values))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
