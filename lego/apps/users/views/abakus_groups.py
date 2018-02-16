from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.users import constants
from lego.apps.users.filters import AbakusGroupFilterSet
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.abakus_groups import (
    DetailedAbakusGroupSerializer, PublicAbakusGroupSerializer, PublicDetailedAbakusGroupSerializer,
    PublicListAbakusGroupSerializer
)


class AbakusGroupViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = AbakusGroup.objects.all()
    ordering = 'id'
    filter_class = AbakusGroupFilterSet
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return PublicListAbakusGroupSerializer

        abakus_group = self.get_object()
        if self.action == 'retrieve' and not self.request.user.has_perm(EDIT, abakus_group):
            if abakus_group.type in constants.PUBLIC_GROUPS:
                return PublicDetailedAbakusGroupSerializer
            return PublicAbakusGroupSerializer

        return DetailedAbakusGroupSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return AbakusGroup.objects_with_text \
                .prefetch_related('users') \
                .all()

        return self.queryset
