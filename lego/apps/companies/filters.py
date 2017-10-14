from django_filters import BooleanFilter, FilterSet

from lego.apps.companies.models import Semester


class SemesterFilterSet(FilterSet):
    company_interest = BooleanFilter('active_interest_form')

    class Meta:
        model = Semester
        fields = ('company_interest',)
