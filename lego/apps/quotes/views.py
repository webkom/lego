from lego.apps.quotes.serializers import QuoteSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.quotes.models import Quote
from lego.apps.quotes.permissions import QuotePermissions, QuotePermissionsFilter


class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    filter_backends = (QuotePermissionsFilter, )
    permission_classes = (IsAuthenticated, QuotePermissions)
    serializer_class = QuoteSerializer

    @detail_route(methods=['GET'])
    def like(self, request, pk=None):
        return self._like_quote(request=request)

    @detail_route(methods=['GET'])
    def unlike(self, request, pk=None):
        return self._like_quote(request=request, like=False)

    @detail_route(methods=['PUT'])
    def approve(self, request, pk=None):
        return self._approve_quote(request=request)

    @detail_route(methods=['PUT'])
    def unapprove(self, request, pk=None):
        return self._approve_quote(request=request, approve=False)

    def _like_quote(self, request, like=True):
        instance = self.get_object()
        has_liked = instance.has_liked(user=request.user)
        if like:
            if instance.approved and not has_liked:
                instance.like(user=request.user)
            else:
                # TODO: Raise a 409 instead?
                raise PermissionDenied
        else:
            if instance.approved and has_liked:
                instance.unlike(user=request.user)
            else:
                # TODO: Raise a 409 instead?
                raise PermissionDenied
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def _approve_quote(self, request, approve=True):
        instance = self.get_object()
        if approve:
            instance.approve()
        else:
            instance.unapprove()
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data
        )
