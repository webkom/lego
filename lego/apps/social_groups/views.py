from rest_framework import viewsets

from lego.apps.social_groups.models import InterestGroup
from lego.apps.social_groups.permissions import InterestGroupPermissions
from lego.apps.social_groups.serializers import InterestGroupSerializer


class InterestGroupViewSet(viewsets.ModelViewSet):
    queryset = InterestGroup.group_objects.all()
    serializer_class = InterestGroupSerializer
    permission_classes = (InterestGroupPermissions,)
    ordering = 'id'

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset
