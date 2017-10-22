from django_filters.rest_framework import CharFilter, FilterSet

from lego.apps.email.models import EmailList
from lego.apps.users.models import User


class EmailListFilterSet(FilterSet):

    email = CharFilter(name='email_id')

    class Meta:
        model = EmailList
        fields = ('name', 'email')


class EmailUserFilterSet(FilterSet):

    email = CharFilter(name='internal_email_id')

    class Meta:
        model = User
        fields = ('email',)
