from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from django_filters import BooleanFilter, CharFilter, FilterSet

from lego.apps.companies.models import (
    Company,
    CompanyInterest,
    Semester,
    StudentCompanyContact,
)


class AdminCompanyFilterSet(FilterSet):

    name = CharFilter(method="filter_name")
    student_contacts = CharFilter(method="filter_student_contacts")
    status = CharFilter(method="filter_semester_status")

    def filter_semester_status(self, queryset, name, value):
        if not value:
            return queryset

        statuses = [
            status.strip()
            for status in self.request.query_params.get("status", "").split(",")
        ]
        semester_id = self.request.query_params.get("semester_id")

        if statuses and all(statuses):
            status_q = Q()
            for status in statuses:
                status_q |= Q(
                    semester_statuses__semester_id=semester_id,
                    semester_statuses__contacted_status__contains=[status],
                )

            filtered_queryset = queryset.filter(status_q)

            return filtered_queryset

        return queryset

    def filter_name(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    def filter_student_contacts(self, queryset, name, value):
        if not value:
            return queryset

        semester_id = self.request.query_params.get("semester_id")

        filtered_student_company_contacts = StudentCompanyContact.objects.all()
        if semester_id is not None:
            filtered_student_company_contacts = StudentCompanyContact.objects.filter(
                semester_id=semester_id
            )

        filtered_student_company_contacts = filtered_student_company_contacts.annotate(
            user__fullname=Concat(
                F("user__first_name"), Value(" "), F("user__last_name")
            )
        ).filter(user__fullname__icontains=value)

        filtered_company_ids = filtered_student_company_contacts.values_list(
            "company", flat=True
        )

        return queryset.filter(id__in=filtered_company_ids)

    class Meta:
        model = Company
        fields = ["name", "status", "student_contacts"]


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
