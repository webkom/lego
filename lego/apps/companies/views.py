import csv

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F, Q
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
from lego.apps.events import constants as event_constants
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

    @action(detail=True, methods=["GET"], url_path="event-statistics")
    def event_statistics(self, request, *args, **kwargs):
        company = self.get_object()

        try:
            semesters = [
                Semester.objects.get(pk=int(request.query_params[param]))
                for param in ("from_semester", "to_semester")
            ]
        except (KeyError, ValueError, Semester.DoesNotExist):
            return Response(
                {"detail": "from_semester and to_semester must be valid semester ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_registration = Q(
            registrations__deleted=False,
            registrations__unregistration_date=None,
            registrations__status__in=[
                event_constants.SUCCESS_REGISTER,
                event_constants.FAILURE_UNREGISTER,
            ],
        )
        events = (
            company.events.filter(
                start_time__gte=min(semester.start_time for semester in semesters),
                start_time__lt=max(semester.end_time for semester in semesters),
            )
            .annotate(
                participant_count=Count(
                    "registrations",
                    filter=active_registration & Q(registrations__pool__isnull=False),
                )
                + F("legacy_registration_count"),
                waiting_list_count=Count(
                    "registrations",
                    filter=active_registration & Q(registrations__pool__isnull=True),
                ),
            )
            .values_list("participant_count", "waiting_list_count")
        )

        event_count = len(events)
        return Response(
            {
                "event_count": event_count,
                "average_participants": (
                    sum(participants for participants, _ in events) / event_count
                    if event_count
                    else 0
                ),
                "average_waiting_list": (
                    sum(waiting for _, waiting in events) / event_count
                    if event_count
                    else 0
                ),
            }
        )


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
