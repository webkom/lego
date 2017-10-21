from django_filters.rest_framework import FilterSet

from lego.apps.restricted.models import RestrictedMail


class RestrictedMailFilterSet(FilterSet):

    class Meta:
        model = RestrictedMail
        fields = ('from_address', 'hide_sender', 'token')
