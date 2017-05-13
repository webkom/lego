from rest_framework import filters, viewsets

from lego.apps.permissions.filters import AbakusObjectPermissionFilter
from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import Membership
from lego.apps.users.serializers.memberships import MembershipSerializer


class MembershipViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = MembershipFilterSet
    ordering = 'id'
