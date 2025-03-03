from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import CharFilter, FilterSet

from lego.apps.users.models import User


class AchievementFilterSet(FilterSet):
    userFullname = CharFilter(method="filter_user_fullname")
    abakusGroupName = CharFilter(method="filter_abakus_group_name")

    class Meta:
        model = User
        fields = ("userFullname", "abakusGroupName")

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

    def filter_abakus_group_name(self, queryset, name, value):
        """
        Returns only Users who have an active, non-deleted Membership
        to an AbakusGroup whose name matches `value`.
        """
        if not value:
            return queryset

        return queryset.filter(
            memberships__is_active=True,
            memberships__abakus_group__name__icontains=value,
        ).distinct()
