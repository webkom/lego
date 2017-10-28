from django_filters.rest_framework import CharFilter, FilterSet

from lego.apps.email.models import EmailList
from lego.apps.users.models import User


class EmailListFilterSet(FilterSet):

    name = CharFilter(lookup_expr='icontains')
    email = CharFilter(name='email__email', lookup_expr='icontains')

    class Meta:
        model = EmailList
        fields = ('name', 'email')


class EmailUserFilterSet(FilterSet):

    email = CharFilter(name='internal_email__email', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ('email',)
