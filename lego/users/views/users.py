# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lego.permissions.model_permissions import PostDeleteModelPermissions
from lego.users.models import User
from lego.users.permissions import UsersObjectPermissions
from lego.users.serializers import UserSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, PostDeleteModelPermissions, UsersObjectPermissions)
