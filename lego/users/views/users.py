# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.users.models import User
from lego.users.serializers import UserSerializer, PublicUserSerializer
from lego.users.permissions import AbakusModelPermissions


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, AbakusModelPermissions)

    def list(self, request, *args, **kwargs):
        if (not request.user.is_superuser
                and not request.user.has_perm('users.list_user')):

            raise PermissionDenied()

        return super(UsersViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)

        if (not request.user.is_superuser
                and not request.user.has_perm('users.retrieve_user')
                and self.get_object_or_none() != request.user):

            serializer = PublicUserSerializer(user)
        else:
            serializer = UserSerializer(user)

        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        if (not request.user.is_superuser
                and not request.user.has_perm('users.change_user')
                and request.user.pk != pk):

            raise PermissionDenied()

        return super(UsersViewSet, self).update(request, *args, **kwargs)
