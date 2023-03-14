from django_filters import BooleanFilter, CharFilter, FilterSet

from lego.apps.companies.models import CompanyInterest, Semester


class SemesterFilterSet(FilterSet):
    company_interest = BooleanFilter("active_interest_form")

    class Meta:
        model = Semester
        fields = ("company_interest",)


class CompanyInterestFilterSet(FilterSet):
    events = CharFilter(lookup_expr="icontains")

    class Meta:
        model = CompanyInterest
        fields = ("semesters", "events")
