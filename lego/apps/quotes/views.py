from rest_framework import filters, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from lego.apps.quotes.filters import QuoteModelFilter, QuotesFilterSet
from lego.apps.quotes.models import Quote
from lego.apps.quotes.permissions import QuotePermissions
from lego.apps.quotes.serializers import QuoteSerializer


class QuoteViewSet(viewsets.ModelViewSet):

    queryset = Quote.objects.all()
    filter_backends = (filters.DjangoFilterBackend, QuoteModelFilter)
    filter_class = QuotesFilterSet
    permission_classes = (QuotePermissions, )
    serializer_class = QuoteSerializer

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
