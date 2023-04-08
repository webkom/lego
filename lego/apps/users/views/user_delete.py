from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.users.serializers.user_delete import UserDeleteSerializer


class UserDeleteViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = UserDeleteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.delete(force=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
