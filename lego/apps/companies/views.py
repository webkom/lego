import csv

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from lego.apps.companies.filters import CompanyInterestFilterSet, SemesterFilterSet
from lego.apps.companies.models import (
    Company,
    CompanyContact,
    CompanyFile,
    CompanyInterest,
    Semester,
    SemesterStatus,
)
from lego.apps.companies.permissions import CompanyAdminPermissionHandler
from lego.apps.companies.serializers import (
    CompanyAdminDetailSerializer,
    CompanyAdminListSerializer,
    CompanyContactSerializer,
    CompanyDetailSerializer,
    CompanyFileSerializer,
    CompanyInterestCreateAndUpdateSerializer,
    CompanyInterestListSerializer,
    CompanyInterestSerializer,
    CompanyListSerializer,
    SemesterSerializer,
    SemesterStatusDetailSerializer,
    SemesterStatusSerializer,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT

from .constants import (
    AUTUMN,
    SPRING,
    TRANSLATED_COLLABORATIONS,
    TRANSLATED_EVENTS,
    TRANSLATED_OTHER_OFFERS,
)


class AdminCompanyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = (
        Company.objects.all()
        .prefetch_related("semester_statuses", "files")
        .select_related("student_contact")
    )
    pagination_class = None
    permission_handler = CompanyAdminPermissionHandler()

    def get_serializer_class(self):
        return (
            CompanyAdminListSerializer
            if self.action == "list"
            else CompanyAdminDetailSerializer
        )


class CompanyViewSet(
    AllowedPermissionsMixin,
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Company.objects.all().filter(active=True)
    ordering = "name"

    def get_serializer_class(self):
        return (
            CompanyListSerializer if self.action == "list" else CompanyDetailSerializer
        )

    @action(detail=True, methods=["GET"])
    def csv(self, *args, **kwargs):
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Company)

        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        semester_year = kwargs["pk"].split("_")
        semester = Semester.objects.get(
            year=semester_year[0], semester=semester_year[1]
        )

        if len(semester_year) == 3:
            companyInterests = CompanyInterest.objects.filter(
                semesters__in=[semester]
            ).filter(events__contains=[semester_year[2]])
        else:
            companyInterests = CompanyInterest.objects.filter(semesters__in=[semester])

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{kwargs["pk"]}.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Company name:",
                "Contact person:",
                "Mail:",
                "Phone",
                "Company info",
                "Semesters:",
                "Events:",
                "Other offers:",
                "Collaborations:",
                "Company type:",
                "Company course themes:",
                "Accommodating in Trondheim:",
                "Target grades:",
                "participant range:",
                "Company info:",
                "Course comment:",
                "Breakfast talk comment:",
                "Other event comment:",
                "Startup comment:",
                "Company to company comment:",
                "Lunch presentation comment:",
                "Company presentation comment:",
                "Bedex comment:",
            ]
        )
        for ci in companyInterests:
            writer.writerow(
                [
                    ci.company_name,
                    ci.contact_person,
                    ci.mail,
                    ci.phone,
                    ci.comment,
                    [
                        f"Vår {semester.year}"
                        if semester.semester == SPRING
                        else f"Høst {semester.year}"
                        for semester in ci.semesters.all()
                    ],
                    ", ".join([TRANSLATED_EVENTS[event] for event in ci.events]),
                    ", ".join(
                        [TRANSLATED_OTHER_OFFERS[offer] for offer in ci.other_offers]
                    ),
                    ", ".join(
                        [
                            TRANSLATED_COLLABORATIONS[collab]
                            for collab in ci.collaborations
                        ]
                    ),
                    ci.company_type,
                    ", ".join(ci.company_course_themes),
                    ci.office_in_trondheim,
                    ", ".join([f"{grade}.kl" for grade in ci.target_grades]),
                    f"{ci.participant_range_start} - {ci.participant_range_end}",
                    ci.course_comment,
                    ci.breakfast_talk_comment,
                    ci.other_event_comment,
                    ci.startup_comment,
                    ci.company_to_company_comment,
                    ci.lunch_presentation_comment,
                    ci.company_presentation_comment,
                    ci.bedex_comment,
                ]
            )

        return response


class CompanyFilesViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyFile.objects.all()
    serializer_class = CompanyFileSerializer
    ordering = "id"

    def get_queryset(self):
        if self.request is None:
            return CompanyFile.objects.none()

        company_id = self.kwargs["company_pk"]
        return CompanyFile.objects.filter(company=company_id)


class SemesterStatusViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = SemesterStatus.objects.all()
    serializer_class = SemesterStatusDetailSerializer

    def get_queryset(self):
        if self.request is None:
            return SemesterStatus.objects.none()

        company_id = self.kwargs["company_pk"]
        return SemesterStatus.objects.filter(company=company_id)

    def get_serializer_class(self):
        if self.action == "list":
            return SemesterStatusSerializer

        return super().get_serializer_class()


class CompanyContactViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer

    def get_queryset(self):
        if self.request is None:
            return CompanyContact.objects.none()

        company_id = self.kwargs["company_pk"]
        return CompanyContact.objects.filter(company=company_id)


class SemesterViewSet(viewsets.ModelViewSet):
    filterset_class = SemesterFilterSet

    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    pagination_class = None


class CompanyInterestViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    """
    Used by new companies to register interest in Abakus and our services.
    """

    ordering = "-created_at"
    queryset = CompanyInterest.objects.all()
    filterset_class = CompanyInterestFilterSet

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyInterestListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CompanyInterestCreateAndUpdateSerializer
        return CompanyInterestSerializer
