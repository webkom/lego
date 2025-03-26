import csv

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from lego.apps.companies.filters import (
    AdminCompanyFilterSet,
    CompanyFilterSet,
    CompanyInterestFilterSet,
    SemesterFilterSet,
)
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
    SPRING,
    TRANSLATED_COLLABORATIONS,
    TRANSLATED_COMPANY_TYPES,
    TRANSLATED_COURSE_THEMES,
    TRANSLATED_EVENTS,
    TRANSLATED_OTHER_OFFERS,
)


class AdminCompanyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related("semester_statuses", "files")
    filterset_class = AdminCompanyFilterSet
    permission_handler = CompanyAdminPermissionHandler()
    ordering_fields = ["name", "created_at"]
    ordering = "name"

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "list":
            semester_id = self.request.query_params.get("semester_id", None)
            context.update({"semester_id": semester_id})

        return context

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyAdminListSerializer

        return CompanyAdminDetailSerializer


class CompanyViewSet(
    AllowedPermissionsMixin,
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Company.objects.all().filter(active=True)
    filterset_class = CompanyFilterSet
    ordering = "name"

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        return CompanyDetailSerializer


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

    @action(detail=False, methods=["GET"])
    def csv(self, *args, **kwargs):
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Company)
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        year = self.request.query_params.get("year")
        semester = self.request.query_params.get("semester")
        event = self.request.query_params.get("event")

        try:
            semester = Semester.objects.get(year=year, semester=semester)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        companyInterests = CompanyInterest.objects.filter(semesters__in=[semester])
        if event:
            companyInterests = companyInterests.filter(events__contains=[event])

        event_string = f"-{event}" if event else ""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{f"Company-interests-{year}-{semester}{event_string}"}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Navn på bedrift",
                "Kontaktperson",
                "E-post",
                "Telefonnummer",
                "Bedriftsinformasjon",
                "Semester",
                "Arrangementer",
                "Annet",
                "Samarbeid",
                "Bedriftstype",
                "Relevante temaer",
                "Kontorer i Trondheim for besøk",
                "Ønsker torsdagsarrangement",
                "Klassetrinn",
                "Antall deltagere",
                "Faglig arrangement kommentar",
                "Frokostforedrag kommentar",
                "Alternativt arrangement kommentar",
                "Start-up kommentar",
                "Bedrift-til-bedrift kommentar",
                "Lunsjpresentasjon kommentar",
                "Bedriftspresentasjon kommentar",
                "BedEx kommentarg",
            ]
        )
        for companyInterest in companyInterests:
            company_name = (
                companyInterest.company.name
                if companyInterest.company
                else companyInterest.company_name
            )
            participant_range_start = companyInterest.participant_range_start
            participant_range_end = companyInterest.participant_range_end
            semesters = ", ".join(
                [
                    (
                        f"Vår {semester.year}"
                        if semester.semester == SPRING
                        else f"Høst {semester.year}"
                    )
                    for semester in companyInterest.semesters.all()
                ]
            )
            events = (
                ", ".join(
                    [TRANSLATED_EVENTS[event] for event in companyInterest.events]
                )
                if companyInterest.events
                else ""
            )
            other_offers = (
                ", ".join(
                    [
                        TRANSLATED_OTHER_OFFERS[offer]
                        for offer in companyInterest.other_offers
                    ]
                )
                if companyInterest.other_offers
                else ""
            )
            collaborations = (
                ", ".join(
                    [
                        TRANSLATED_COLLABORATIONS[collab]
                        for collab in companyInterest.collaborations
                    ]
                )
                if companyInterest.collaborations
                else ""
            )
            company_course_themes = (
                ", ".join(
                    [
                        TRANSLATED_COURSE_THEMES[course_theme]
                        for course_theme in companyInterest.company_course_themes
                    ]
                )
                if companyInterest.company_course_themes
                else ""
            )
            target_grades = (
                ", ".join([f"{grade}.kl" for grade in companyInterest.target_grades])
                if companyInterest.target_grades
                else ""
            )
            company_type = (
                TRANSLATED_COMPANY_TYPES[companyInterest.company_type]
                if companyInterest.company_type
                else ""
            )
            office_in_trondheim = (
                companyInterest.office_in_trondheim
                if companyInterest.office_in_trondheim
                else ""
            )
            wants_thursday_event = (
                companyInterest.wants_thursday_event
                if companyInterest.wants_thursday_event
                else ""
            )
            writer.writerow(
                [
                    company_name,
                    companyInterest.contact_person,
                    companyInterest.mail,
                    companyInterest.phone,
                    companyInterest.comment,
                    semesters,
                    events,
                    other_offers,
                    collaborations,
                    company_type,
                    company_course_themes,
                    office_in_trondheim,
                    wants_thursday_event,
                    target_grades,
                    f"{participant_range_start} - {participant_range_end}",
                    companyInterest.course_comment,
                    companyInterest.breakfast_talk_comment,
                    companyInterest.other_event_comment,
                    companyInterest.startup_comment,
                    companyInterest.company_to_company_comment,
                    companyInterest.lunch_presentation_comment,
                    companyInterest.company_presentation_comment,
                    companyInterest.bedex_comment,
                ]
            )

        return response
