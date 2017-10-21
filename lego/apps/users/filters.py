from django_filters import CharFilter, FilterSet

from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory


class MembershipFilterSet(FilterSet):
    group = CharFilter(name='abakus_group')

    class Meta:
        model = Membership
        fields = ('group',)


class AbakusGroupFilterSet(FilterSet):

    class Meta:
        model = AbakusGroup
        fields = ('type',)


class MembershipHistoryFilterSet(FilterSet):

    class Meta:
        model = MembershipHistory
        fields = ('user', 'abakus_group', 'role')
