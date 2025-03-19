import csv
import os

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from weasyprint import HTML

from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.surveys.authentication import SurveyTokenAuthentication
from lego.apps.surveys.constants import TEXT_FIELD
from lego.apps.surveys.filters import SubmissionFilterSet, SurveyFilterSet
from lego.apps.surveys.models import Answer, Submission, Survey
from lego.apps.surveys.serializers import (
    SubmissionAdminReadSerializer,
    SubmissionCreateAndUpdateSerializer,
    SubmissionReadSerializer,
    SurveyCreateSerializer,
    SurveyReadDetailedAdminSerializer,
    SurveyReadDetailedSerializer,
    SurveyReadSerializer,
    SurveyUpdateSerializer,
)
from lego.apps.surveys.utils.report_utils import (
    describe_results_csv,
    describe_results_with_charts,
)


class SurveyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Survey.objects.all().prefetch_related("questions", "submissions")
    permission_classes = [LegoPermissions, IsAuthenticated]
    filterset_class = SurveyFilterSet
    filter_backends = (DjangoFilterBackend,)

    ordering = ("-active_from", "title")

    def get_queryset(self):
        if self.request is None:
            return Survey.objects.none()

        user = self.request.user
        permission_handler = get_permission_handler(Survey)
        return permission_handler.filter_queryset(
            user,
            queryset=Survey.objects.prefetch_related("questions", "submissions"),
        )

    def get_serializer_class(self):
        if self.action in ["create"]:
            return SurveyCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return SurveyUpdateSerializer
        elif self.action in ["retrieve"]:
            user = self.request.user
            is_admin = user.has_perm(EDIT, obj=Survey)
            return (
                SurveyReadDetailedAdminSerializer
                if is_admin
                else SurveyReadDetailedSerializer
            )
        return SurveyReadSerializer

    @action(detail=True, methods=["POST"])
    def share(self, *args, **kwargs):
        survey = Survey.objects.get(pk=kwargs["pk"])
        survey.generate_token()
        serializer = SurveyReadDetailedAdminSerializer(survey)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["POST"])
    def hide(self, *args, **kwargs):
        survey = Survey.objects.get(pk=kwargs["pk"])
        survey.delete_token()
        serializer = SurveyReadDetailedAdminSerializer(survey)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["GET"])
    def csv(self, *args, **kwargs):
        survey = Survey.objects.get(pk=kwargs["pk"])
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{survey.title.replace(" ", "_")}.csv"'
        )

        writer = csv.writer(response)
        for question in describe_results_csv(survey):
            for line in question:
                writer.writerow(line)
            writer.writerow([])

        return response

    @action(detail=True, methods=["GET"])
    def pdf(self, *args, **kwargs):
        survey = Survey.objects.get(pk=kwargs["pk"])
        charts_data = describe_results_with_charts(survey)

        context = {
            "survey_title": survey.title,
            "charts_data": charts_data,
            "logo_image_path": os.path.join(
                settings.STATIC_ROOT, "assets/img/abakus.png"
            ),
            "hsp_image_path": os.path.join(
                settings.STATIC_ROOT, "assets/img/bekk_short_black.svg"
            ),
            "company": survey.event.company.name if survey.event.company else "N/A",
            "date": survey.event.start_time.strftime("%Y-%m-%d"),
        }

        html_string = render_to_string(
            "surveys/pdf/survey_report_template.html", context
        )

        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{survey.title.replace(" ", "_")}.pdf"'
        )
        return response


class SurveyTemplateViewSet(
    AllowedPermissionsMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = (
        Survey.objects.all().prefetch_related("questions").filter(is_template=True)
    )
    lookup_field = "id"
    permission_classes = [LegoPermissions, IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return SurveyReadDetailedSerializer
        return SurveyReadSerializer


class SubmissionViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    permission_classes = [LegoPermissions, IsAuthenticated]
    filterset_class = SubmissionFilterSet
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        if self.request is None:
            return Submission.objects.none()

        survey_id = self.kwargs["survey_pk"]
        permission_handler = get_permission_handler(Submission)
        return permission_handler.filter_queryset(
            self.request.user, Submission.objects.filter(survey_id=survey_id)
        )

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return SubmissionCreateAndUpdateSerializer
        if self.request and self.request.user.has_perm(EDIT, obj=Survey):
            return SubmissionAdminReadSerializer
        return SubmissionReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            SubmissionReadSerializer(
                serializer.instance, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def validate_answer(self, request, **kwargs):
        submission = Submission.objects.get(pk=kwargs["pk"])
        answer_pk = request.query_params.get("answer")
        if answer_pk is None:
            raise exceptions.NotAcceptable("No answer specified")
        try:
            answer = submission.answers.get(pk=answer_pk)
        except Answer.DoesNotExist as e:
            raise exceptions.NotFound("Answer not found") from e
        if answer.question.question_type != TEXT_FIELD:
            raise exceptions.NotAcceptable("Only text answers can be hidden")
        return submission, answer

    @action(detail=True, methods=["POST"])
    def hide(self, request, **kwargs):
        submission, answer = self.validate_answer(request, **kwargs)
        answer.hide()
        return Response(
            data=SubmissionAdminReadSerializer(
                submission, context={"request": request}
            ).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["POST"])
    def show(self, request, **kwargs):
        submission, answer = self.validate_answer(request, **kwargs)
        answer.show()
        return Response(
            data=SubmissionAdminReadSerializer(
                submission, context={"request": request}
            ).data,
            status=status.HTTP_202_ACCEPTED,
        )


class SurveyTokenViewset(viewsets.GenericViewSet):
    authentication_classes = [SurveyTokenAuthentication]
    permission_classes = [LegoPermissions]
    queryset = Survey.objects.all()

    def retrieve(self, request, pk):
        survey = self.get_object()
        serialized_survey = SurveyReadDetailedSerializer(survey).data
        serialized_survey["results"] = survey.aggregate_submissions()
        serialized_survey["submissionCount"] = survey.submissions.count()
        return Response(data=serialized_survey)
