from django.db.models import F, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import CharFilter, FilterSet

from lego.apps.users.models import AbakusGroup, Membership, MembershipHistory, Penalty


class MembershipFilterSet(FilterSet):

    userUsername = CharFilter(field_name="user__username", lookup_expr="icontains")
    userFullname = CharFilter(field_name="userFullname", method="user__fullname")
    abakusGroupName = CharFilter(
        field_name="abakus_group__name", lookup_expr="icontains"
    )

    class Meta:
        model = Membership
        fields = (
            "role",
            "userUsername",
            "abakusGroupName",
            "userFullname",
        )

    def user__fullname(self, queryset, name, value):
        if value:
            return queryset.annotate(
                user__fullname=Concat(
                    F("user__first_name"), Value(" "), F("user__last_name")
                )
            ).filter(user__fullname__icontains=value)
        return queryset


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
