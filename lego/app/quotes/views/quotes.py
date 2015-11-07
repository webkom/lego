from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.app.quotes.models import Quote, QuoteLike
from lego.app.quotes.permissions import QuotePermissions
from lego.app.quotes.serializers import QuoteLikeSerializer, QuoteSerializer
from lego.permissions.filters import ObjectPermissionsFilter


class QuoteViewSet(viewsets.ModelViewSet):
    def get_object(self, pk=None):
        try:
            return Quote.objects.get(pk=pk)
        except Quote.DoesNotExist:
            raise Http404

    def get_serializer_class(self):
        return QuoteSerializer

    queryset = Quote.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (IsAuthenticated, QuotePermissions)

    def get_queryset(self):
        if self.request.query_params.get('approved') == 'false' \
                and not self.request.user.has_perm(QuotePermissions.perms_map['approve']):
            raise PermissionDenied()
        approved = not (self.request.query_params.get('approved') == 'false' and
                        self.request.user.has_perm(QuotePermissions.perms_map['approve']))
        return Quote.objects.filter(approved=approved)

    def retrieve(self, request, pk=None):
        instance = self.get_object(pk)
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data
        )

    @detail_route(methods=['POST'], url_path='like')
    def like(self, request, pk=None):
        data = {
            'quote': pk,
            'user': request.user.id
        }
        serializer = QuoteLikeSerializer(data=data)
        if serializer.is_valid():
            return self._likeQuote(request=request, pk=pk)
        else:
            # TODO: Not found 404?
            raise ValidationError(serializer.errors)

    @detail_route(methods=['POST'], url_path='unlike')
    def unlike(self, request, pk=None):
        return self._likeQuote(request=request, pk=pk, like=False)

    @detail_route(methods=['PUT'], url_path='approve')
    def approve(self, request, pk=None):
        return self._approveQuote(request=request, pk=pk)

    @detail_route(methods=['PUT'], url_path='unapprove')
    def unapprove(self, request, pk=None):
        return self._approveQuote(request=request, pk=pk, approve=False)

    def _likeQuote(self, request, pk, like=True):
        instance = self.get_object(pk)
        if like:
            quote_like = bool(QuoteLike.objects.filter(user=request.user, quote=instance))
            if instance.approved and not quote_like:
                instance.like(user=request.user)
            else:
                # TODO: Raise a 409 instead?
                raise PermissionDenied
        else:
            quote_like = bool(QuoteLike.objects.filter(user=request.user, quote=instance))
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

    def _approveQuote(self, request, pk, approve=True):
        instance = self.get_object(pk)
        if approve:
            instance.approve()
        else:
            instance.unapprove()
        serializer = QuoteSerializer(instance, context={'request': request})
        return Response(
            serializer.data
        )
