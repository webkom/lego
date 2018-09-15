from django_filters import BooleanFilter, CharFilter, FilterSet, NumberFilter

from lego.apps.companies.models import Semester, CompanyInterest


class SemesterFilterSet(FilterSet):
    company_interest = BooleanFilter('active_interest_form')

    class Meta:
        model = Semester
        fields = ('company_interest', )

class CompanyInterestFilterSet(FilterSet):
    semester = CharFilter('semester')
    year = NumberFilter('year')

    class Meta:
        model = CompanyInterest
        fields = ('semester', 'year')
