# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

from lego.users.models import User
from lego.users.serializers import UserSerializer, PublicUserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)

        if not request.user.is_superuser:
            serializer = PublicUserSerializer(user)
        else:
            serializer = UserSerializer(user)

        return Response(serializer.data)

