from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.users.models import User
from lego.apps.users.permissions import UsersPermissions
from lego.apps.users.serializers.users import MeSerializer, UserSerializer


class UsersViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, UsersPermissions)
    ordering = 'id'

    @list_route(
        methods=['GET'], permission_classes=[IsAuthenticated],
        serializer_class=MeSerializer
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
