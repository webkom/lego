from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.users.serializers.password_change import ChangePasswordSerializer


class ChangePasswordViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.validated_data['new_password'])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
