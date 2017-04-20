from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lego.apps.users.models import AbakusGroup
from lego.apps.users.permissions import AbakusGroupPermissions
from lego.apps.users.serializers.abakus_groups import AbakusGroupSerializer


class AbakusGroupViewSet(viewsets.ModelViewSet):
    queryset = AbakusGroup.objects.all()
    serializer_class = AbakusGroupSerializer
    permission_classes = (IsAuthenticated, AbakusGroupPermissions)
    ordering = 'id'

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset
