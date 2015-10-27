from django.contrib.auth.models import AnonymousUser
from django.core import serializers
from lego.users.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.app.quotes.models import Quote
from lego.app.quotes.permissions import QuotePermissions
from lego.app.quotes.serializers import (QuoteCreateAndUpdateSerializer,
                                         QuoteLikeSerializer, QuoteApprovedReadSerializer,
                                         QuoteUnapprovedReadSerializer)
from lego.permissions.filters import ObjectPermissionsFilter


class QuoteViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return QuoteCreateAndUpdateSerializer
        return QuoteApprovedReadSerializer

    queryset = Quote.objects.all()
    filter_backends = (ObjectPermissionsFilter,)
    permission_classes = (IsAuthenticated, QuotePermissions)

    def get_queryset(self):
         return Quote.objects.filter(approved=True)

    @list_route()
    def unapproved(self, request):
        if not self.request.user.has_perm(QuotePermissions.perms_map['approve']):
            raise PermissionDenied()
        quotes = Quote.objects.filter(approved=False)
        serialized_quotes = []
        for instance in quotes:
            serializer = QuoteUnapprovedReadSerializer(instance, context={'request': request})
            serialized_quotes.append(serializer.data)
        return Response(
            serialized_quotes,
            status=status.HTTP_200_OK
        )

    @detail_route(methods=['POST'], url_path='like')
    def like(self, request, pk=None):
        if not self.request.user.has_perm(QuotePermissions.perms_map['like']):
            raise PermissionDenied()
        data = {
            'quote': pk,
            'user': request.user.id
        }
        serializer = QuoteLikeSerializer(data=data)
        if serializer.is_valid():
            instance = self.get_object()
            if not instance.is_approved():
                raise PermissionDenied()
            instance.like(user=request.user)
            serializer = QuoteApprovedReadSerializer(instance, context={'request': request}) #TODO: different serializer?
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            #TODO: Not found 404?
            raise ValidationError(serializer.errors)

    @detail_route(methods=['POST'], url_path='unlike')
    def unlike(self, request, pk=None):
        if not self.request.user.has_perm(QuotePermissions.perms_map['like']):
            raise PermissionDenied()
        instance = self.get_object()
        if not instance.is_approved():
            raise PermissionDenied()
        result = instance.unlike(user=request.user)
        # TODO: do something with result?
        serializer = QuoteApprovedReadSerializer(instance, context={'request': request}) #TODO: different serializer?
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @detail_route(methods=['PUT'], url_path='approve')
    def approve(self, request, pk=None):
        if not self.request.user.has_perm(QuotePermissions.perms_map['approve']):
            raise PermissionDenied()
        instance = self.get_object()
        result = instance.approve()
        # TODO: do something with result?
        serializer = QuoteApprovedReadSerializer(instance, context={'request': request}) #TODO: different serializer?
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @detail_route(methods=['PUT'], url_path='unapprove')
    def unapprove(self, request, pk=None):
        if not self.request.user.has_perm(QuotePermissions.perms_map['approve']):
            raise PermissionDenied()
        instance = self.get_object()
        result = instance.unapprove()
        # TODO: do something with result?

        serializer = QuoteApprovedReadSerializer(instance, context={'request': request}) #TODO: different serializer?
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )