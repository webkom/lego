from rest_framework import viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import Membership
from lego.apps.users.serializers.memberships import MembershipSerializer


class MembershipViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Membership.objects.all().select_related('user')
    serializer_class = MembershipSerializer
    filter_class = MembershipFilterSet
    ordering = 'id'
