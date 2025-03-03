from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import CharFilter, FilterSet

from lego.apps.users.models import User


class AchievementFilterSet(FilterSet):
    userFullName = CharFilter(method="filter_user_fullname")
    abakusGroupIds = CharFilter(method="filter_abakus_group_ids")

    class Meta:
        model = User
        fields = ("userFullName", "abakusGroupIds")

    def filter_user_fullname(self, queryset, name, value):
        if value:
            return (
                queryset.annotate(
                    fullname=Concat(F("first_name"), Value(" "), F("last_name"))
                )
                .filter(fullname__icontains=value)
                .distinct()
            )
        return queryset
   
    def filter_abakus_group_ids(self, queryset, name, value):
        """
        returns only users who have an active, non-deleted membership
        in *any* of the abakusgroup ids listed in the comma-separated
        query param, e.g. ?abakusgroupids=1,2,3
        """
        if not value:
            return queryset

        group_ids = [part.strip() for part in value.split(",")]
        group_ids = [int(x) for x in group_ids if x.isdigit()]

        return (
            queryset.filter(
                memberships__is_active=true,
                memberships__abakus_group__id__in=group_ids
            )
            .distinct()
        )

