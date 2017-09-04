from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.abakus_groups import AbakusGroupSerializer


class AbakusGroupViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = AbakusGroup.objects.all()
    serializer_class = AbakusGroupSerializer
    ordering = 'id'

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset
