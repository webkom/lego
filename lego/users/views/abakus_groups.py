from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lego.users.models import AbakusGroup
from lego.users.permissions import AbakusGroupPermissions
from lego.users.serializers import AbakusGroupSerializer


class AbakusGroupViewSet(viewsets.ModelViewSet):
    queryset = AbakusGroup.group_objects.all()
    serializer_class = AbakusGroupSerializer
    permission_classes = (IsAuthenticated, AbakusGroupPermissions)

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset
