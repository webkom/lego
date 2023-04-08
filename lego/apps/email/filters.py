from django.db.models import F, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from lego.apps.email.models import EmailList
from lego.apps.users.constants import GROUP_COMMITTEE, GROUP_GRADE
from lego.apps.users.models import User


class EmailListFilterSet(FilterSet):
    name = CharFilter(lookup_expr="icontains")
    email = CharFilter(lookup_expr="icontains", field_name="email__email")
    requireInternalAddress = BooleanFilter(field_name="require_internal_address")

    class Meta:
        model = EmailList
        fields = ("name", "email", "requireInternalAddress")


class EmailUserFilterSet(FilterSet):
    email = CharFilter(field_name="internal_email__email", lookup_expr="icontains")
    userUsername = CharFilter(field_name="username", lookup_expr="icontains")
    userFullname = CharFilter(field_name="userFullname", method="fullname")
    userCommittee = CharFilter(field_name="userCommitee", method="commitee")
    userGrade = CharFilter(field_name="abakus_groups", method="grade")
    enabled = BooleanFilter(field_name="internal_email_enabled")

    def grade(self, queryset, name, value):
        if value == "-":
            return queryset.exclude(abakus_groups__type=GROUP_GRADE)
        if value:
            return queryset.filter(
                abakus_groups__name__icontains=value, abakus_groups__type=GROUP_GRADE
            )
        return queryset

    def commitee(self, queryset, name, value):
        if value == "-":
            return queryset.exclude(abakus_groups__type=GROUP_COMMITTEE)
        if value:
            return queryset.filter(
                abakus_groups__name__icontains=value,
                abakus_groups__type=GROUP_COMMITTEE,
            )
        return queryset

    def fullname(self, queryset, name, value):
        if value:
            return queryset.annotate(
                fullname=Concat(F("first_name"), Value(" "), F("last_name"))
            ).filter(fullname__icontains=value)
        return queryset

    class Meta:
        model = User
        fields = (
            "email",
            "enabled",
            "userUsername",
            "userFullname",
            "userGrade",
            "userCommittee",
        )
