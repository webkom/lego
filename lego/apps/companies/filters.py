from django.db.models import Q
from django_filters import BooleanFilter, CharFilter, FilterSet

from lego.apps.companies.models import Company, CompanyInterest, Semester

class AdminCompanyFilterSet(FilterSet):

    search = CharFilter(method="filter_search")
    show_inactive = BooleanFilter(method="filter_inactive")

    def filter_inactive(self, queryset, name, value):
        if not value:
            return queryset.filter(active=True)
        return queryset

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    class Meta:
        model = Company
        fields = ["search", "show_inactive"]

class CompanyFilterSet(FilterSet):
    search = CharFilter(method="filter_search")
    show_inactive = BooleanFilter(method="filter_inactive")

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    def filter_inactive(self, queryset, name, value):
        if not value:
            return queryset.filter(active=True)
        return queryset

    class Meta:
        model = Company
        fields = ["search", "show_inactive"]


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
