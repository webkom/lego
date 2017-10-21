from rest_framework import mixins, permissions, viewsets

from lego.apps.permissions.constants import EDIT
from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_INTEREST
from lego.apps.users.filters import MembershipHistoryFilterSet
from lego.apps.users.models import Membership, MembershipHistory
from lego.apps.users.serializers.membership_history import MembershipHistorySerializer


class MembershipHistoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                               viewsets.GenericViewSet):

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = MembershipHistorySerializer
    filter_class = MembershipHistoryFilterSet
    ordering = 'id'

    def get_queryset(self):
        queryset = MembershipHistory.objects.all().select_related('user', 'abakus_group')

        if not self.request.user.has_perm(EDIT, Membership):
            return queryset.filter(abakus_group__type__in=(GROUP_COMMITTEE, GROUP_INTEREST))

        return queryset
