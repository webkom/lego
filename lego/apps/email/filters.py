from django_filters.rest_framework import BooleanFilter, CharFilter, FilterSet

from lego.apps.email.models import EmailList
from lego.apps.users.models import User


class EmailListFilterSet(FilterSet):

    name = CharFilter(lookup_expr="icontains")
    email = CharFilter(field_name="email__email", lookup_expr="icontains")
    userFirstName = CharFilter(
        field_name="internal_email__user__last_name", lookup_expr="icontains"
    )
    userLastName = CharFilter(
        field_name="internal_email__user__first_name", lookup_expr="icontains"
    )
    userUsername = CharFilter(field_name="user__username", lookup_expr="icontains")

    class Meta:
        model = EmailList
        fields = ("name", "email", "userFirstName", "userLastName", "userUsername")


class EmailUserFilterSet(FilterSet):

    email = CharFilter(field_name="internal_email__email", lookup_expr="icontains")
    userFirstName = CharFilter(
        field_name="internal_email__user__last_name", lookup_expr="icontains"
    )
    userLastName = CharFilter(
        field_name="internal_email__user__first_name", lookup_expr="icontains"
    )
    enabled = BooleanFilter(field_name="internal_email_enabled")

    class Meta:
        model = User
        fields = ("email", "enabled", "userFirstName", "userLastName")
