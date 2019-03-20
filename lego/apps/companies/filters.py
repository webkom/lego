from django_filters import BooleanFilter, FilterSet

from lego.apps.companies.models import CompanyInterest, Semester


class SemesterFilterSet(FilterSet):
    company_interest = BooleanFilter("active_interest_form")

    class Meta:
        model = Semester
        fields = ("company_interest",)


class CompanyInterestFilterSet(FilterSet):
    class Meta:
        model = CompanyInterest
        fields = ("semesters",)
