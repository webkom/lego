from rest_framework import filters, viewsets

from lego.apps.permissions.filters import AbakusObjectPermissionFilter
from lego.apps.users.filters import MembershipFilterSet
from lego.apps.users.models import Membership
from lego.apps.users.serializers import MembershipSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    filter_class = MembershipFilterSet
    ordering = 'id'
