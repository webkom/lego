from django_filters.rest_framework import filterset
from django_filters.rest_framework import BaseInFilter, CharFilter, FilterSet

from lego.apps.users.models import User


class AchievementFilterSet(filterset.FilterSet):
    userUsername = CharFilter(field_name="user__username", lookup_expr="icontains")
    abakusGroupName = CharFilter(
        field_name="abakus_group__name", lookup_expr="icontains"
    )

    class Meta:
        model = User
        fields = (
            "userUsername",
            "abakusGroupName",
        )
