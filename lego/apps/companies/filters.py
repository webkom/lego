from django.db.models import Exists, F, OuterRef, Q, Value
from django.db.models.functions import Concat
from django_filters import BooleanFilter, CharFilter, FilterSet

from lego.apps.companies.constants import INTERESTED
from lego.apps.companies.models import (
    Company,
    CompanyInterest,
    Semester,
    StudentCompanyContact,
)
from lego.apps.events.models import Event


class AdminCompanyFilterSet(FilterSet):
    name = CharFilter(method="filter_name")
    student_contacts = CharFilter(method="filter_student_contacts")
    status = CharFilter(method="filter_semester_status")

    def filter_semester_status(self, queryset, name, value):
        statuses = {status.strip() for status in value.split(",") if status.strip()}
        if not statuses:
            return queryset

        events = Event.objects.filter(company=OuterRef("pk"), event_type__in=statuses)
        interests = CompanyInterest.objects.filter(company=OuterRef("pk"))

        semester_id = self.request.query_params.get("semester_id")
        if semester_id is not None:
            semester = Semester.objects.filter(pk=semester_id).first()
            if semester is None:
                return queryset.none()
            events = events.filter(
                start_time__gte=semester.start_time, start_time__lt=semester.end_time
            )
            interests = interests.filter(semesters=semester)

        status_q = Exists(events)
        if INTERESTED in statuses:
            status_q |= Exists(interests)

        return queryset.filter(status_q)

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

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value)
        )

    class Meta:
        model = Company
        fields = ["search"]


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
