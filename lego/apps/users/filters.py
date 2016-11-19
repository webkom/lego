from django_filters import CharFilter, FilterSet

from lego.apps.users.models import Membership


class MembershipFilterSet(FilterSet):
    group = CharFilter(name='abakus_group')

    class Meta:
        model = Membership
        fields = ('group',)
