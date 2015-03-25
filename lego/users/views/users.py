# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.permissions.model_permissions import PostDeleteModelPermissions
from lego.users.models import User
from lego.users.permissions import UsersObjectPermissions
from lego.users.serializers import DetailedUserSerializer, UserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, PostDeleteModelPermissions, UsersObjectPermissions)

    @list_route(methods=['GET'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = DetailedUserSerializer(request.user)
        return Response(serializer.data)
