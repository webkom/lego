from django_filters import CharFilter, FilterSet

from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, Penalty


class MembershipFilterSet(FilterSet):
    group = CharFilter(name='abakus_group')

    class Meta:
        model = Membership
        fields = ('group', )


class AbakusGroupFilterSet(FilterSet):
    class Meta:
        model = AbakusGroup
        fields = ('type', )


class MembershipHistoryFilterSet(FilterSet):
    class Meta:
        model = MembershipHistory
        fields = ('user', 'abakus_group', 'role')


class PenaltyFilterSet(FilterSet):
    class Meta:
        model = Penalty
        fields =('user', 'source_event')
