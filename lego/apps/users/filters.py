from django_filters import CharFilter, FilterSet

from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, Penalty


class MembershipFilterSet(FilterSet):

    userFirstName = CharFilter(field_name="user__last_name", lookup_expr="icontains")
    userLastName = CharFilter(field_name="user__first_name", lookup_expr="icontains")
    userUsername = CharFilter(field_name="user__username", lookup_expr="icontains")
    abakusGroupName = CharFilter(
        field_name="abakus_group__name", lookup_expr="icontains"
    )

    class Meta:
        model = Membership
        fields = [
            "role",
            "userFirstName",
            "userLastName",
            "userUsername",
            "abakusGroupName",
        ]


class AbakusGroupFilterSet(FilterSet):
    class Meta:
        model = AbakusGroup
        fields = ("type",)


class MembershipHistoryFilterSet(FilterSet):
    class Meta:
        model = MembershipHistory
        fields = ("user", "abakus_group", "role")


class PenaltyFilterSet(FilterSet):
    class Meta:
        model = Penalty
        fields = ("user", "source_event")
