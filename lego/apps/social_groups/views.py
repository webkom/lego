from rest_framework import viewsets

from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.social_groups.models import InterestGroup
from lego.apps.social_groups.permissions import InterestGroupPermissions
from lego.apps.social_groups.serializers import InterestGroupSerializer


class InterestGroupViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = InterestGroup.objects.all()
    permission_classes = [InterestGroupPermissions]
    serializer_class = InterestGroupSerializer
    ordering = 'id'

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset
