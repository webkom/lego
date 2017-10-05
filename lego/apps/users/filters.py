from django_filters import CharFilter, FilterSet

from lego.apps.users.models import AbakusGroup, Membership


class MembershipFilterSet(FilterSet):
    group = CharFilter(name='abakus_group')

    class Meta:
        model = Membership
        fields = ('group',)


class AbakusGroupFilterSet(FilterSet):

    class Meta:
        model = AbakusGroup
        fields = ('type',)
