from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.app.quotes.models import Quote
from lego.app.quotes.permissions import QuotePermissions
from lego.app.quotes.serializers import (QuoteApprovedReadSerializer,
                                         QuoteCreateAndUpdateSerializer, QuoteLikeSerializer,
                                         QuoteUnapprovedReadSerializer)
from lego.permissions.filters import ObjectPermissionsFilter


class QuoteViewSet(viewsets.ModelViewSet):
    def get_object(self, pk=None):
        try:
            return Quote.objects.get(pk=pk)
        except Quote.DoesNotExist:
            raise Http404

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return QuoteCreateAndUpdateSerializer
        return QuoteApprovedReadSerializer

    queryset = Quote.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (IsAuthenticated, QuotePermissions)

    def get_queryset(self):
        approved = self.request.query_params.get('approved')
        if approved is not None and approved != '' and approved == 'false':
            approved = not self.request.user.has_perm(QuotePermissions.perms_map['approve'])
        else:
            approved = True
        return Quote.objects.filter(approved=approved)

    def retrieve(self, request, pk=None):
        instance = self.get_object(pk)
        serializer = QuoteApprovedReadSerializer(instance, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
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
        if not instance.is_approved():
            raise PermissionDenied()
        if like:
            result = instance.like(user=request.user)
        else:
            result = instance.unlike(user=request.user)
        # TODO: do something with result?
        # TODO: different serializer?
        serializer = QuoteApprovedReadSerializer(instance, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def _approveQuote(self, request, pk, approve=True):
        if not self.request.user.has_perm(QuotePermissions.perms_map['approve']):
            raise PermissionDenied()
        instance = self.get_object(pk)
        if approve:
            result = instance.approve()
        else:
            result = instance.unapprove()
        # TODO: do something with result as it returns True/False if it succeeds/fails.
        serializer = QuoteApprovedReadSerializer(instance, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )