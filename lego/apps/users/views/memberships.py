from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import Membership
from lego.apps.users.serializers.memberships import MembershipSerializer, MembershipCreateSerializer


class MembershipViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Membership.objects.all().select_related('user')
    serializer_class = MembershipSerializer
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = MembershipFilterSet
    ordering = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return MembershipCreateSerializer
        return MembershipSerializer
