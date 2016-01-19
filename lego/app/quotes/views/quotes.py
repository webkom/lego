from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.app.quotes.models import Quote, QuoteLike
from lego.app.quotes.permissions import QuotePermissions
from lego.app.quotes.serializers import QuoteSerializer
from lego.permissions.filters import ObjectPermissionsFilter


class QuoteViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        return QuoteSerializer

    queryset = Quote.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (IsAuthenticated, QuotePermissions)

    def get_queryset(self):
        approved = not (self.request.query_params.get('approved') == 'false' and
                        self.request.user.has_perm(QuotePermissions.perms_map['approve']))
        return Quote.objects.filter(approved=approved)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data
        )

    @detail_route(methods=['POST'], url_path='like')
    def like(self, request, pk=None):
        return self._like_quote(request=request, pk=pk)

    @detail_route(methods=['POST'], url_path='unlike')
    def unlike(self, request, pk=None):
        return self._like_quote(request=request, pk=pk, like=False)

    @detail_route(methods=['PUT'], url_path='approve')
    def approve(self, request, pk=None):
        return self._approve_quote(request=request, pk=pk)

    @detail_route(methods=['PUT'], url_path='unapprove')
    def unapprove(self, request, pk=None):
        return self._approve_quote(request=request, pk=pk, approve=False)

    def _like_quote(self, request, pk, like=True):
        instance = self._get_object(pk)
        quote_like = bool(QuoteLike.objects.filter(user=request.user, quote=instance))
        if like:
            if instance.approved and not quote_like:
                instance.like(user=request.user)
            else:
                # TODO: Raise a 409 instead?
                raise PermissionDenied
        else:
            if instance.approved and quote_like:
                instance.unlike(user=request.user)
            else:
                # TODO: Raise a 409 instead?
                raise PermissionDenied
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def _approve_quote(self, request, pk, approve=True):
        instance = self._get_object(pk)
        if approve:
            instance.approve()
        else:
            instance.unapprove()
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data
        )

    def _get_object(self, pk=None):
        try:
            return Quote.objects.get(pk=pk)
        except Quote.DoesNotExist:
            raise Http404
