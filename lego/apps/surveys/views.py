from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT
from lego.apps.surveys.authentication import SurveyTokenAuthentication
from lego.apps.surveys.constants import TEXT_FIELD
from lego.apps.surveys.filters import SubmissionFilterSet
from lego.apps.surveys.models import Answer, Submission, Survey
from lego.apps.surveys.permissions import (
    SubmissionPermissions,
    SurveyPermissions,
    SurveyTokenPermissions,
)
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


class SurveyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Survey.objects.all().prefetch_related("questions", "submissions")
    permission_classes = [SurveyPermissions]
    filter_backends = (DjangoFilterBackend,)

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
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Survey)
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        survey = Survey.objects.get(pk=kwargs["pk"])
        survey.generate_token()
        serializer = SurveyReadDetailedAdminSerializer(survey)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["POST"])
    def hide(self, *args, **kwargs):
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Survey)
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        survey = Survey.objects.get(pk=kwargs["pk"])
        survey.delete_token()
        serializer = SurveyReadDetailedAdminSerializer(survey)
        return Response(data=serializer.data, status=status.HTTP_202_ACCEPTED)


class SurveyTemplateViewSet(
    AllowedPermissionsMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = (
        Survey.objects.all()
        .prefetch_related("questions")
        .filter(template_type__isnull=False)
    )
    lookup_field = "template_type"
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return SurveyReadDetailedSerializer
        return SurveyReadSerializer


class SubmissionViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    permission_classes = [SubmissionPermissions]
    filter_class = SubmissionFilterSet
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        survey_id = self.kwargs["survey_pk"]
        return Submission.objects.filter(survey=survey_id)

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
            SubmissionReadSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED,
        )

    def validate_answer(self, request, **kwargs):
        submission = Submission.objects.get(pk=kwargs["pk"])
        answer_pk = request.query_params.get("answer")
        if answer_pk is None:
            raise exceptions.NotAcceptable("No answer specified")
        try:
            answer = submission.answers.get(pk=answer_pk)
        except Answer.DoesNotExist:
            raise exceptions.NotFound("Answer not found")
        if answer.question.question_type != TEXT_FIELD:
            raise exceptions.NotAcceptable("Only text answers can be hidden")
        return submission, answer

    @action(detail=True, methods=["POST"])
    def hide(self, request, **kwargs):
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Survey)
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        submission, answer = self.validate_answer(request, **kwargs)
        answer.hide()
        return Response(
            data=SubmissionAdminReadSerializer(submission).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["POST"])
    def show(self, request, **kwargs):
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Survey)
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        submission, answer = self.validate_answer(request, **kwargs)
        answer.show()
        return Response(
            data=SubmissionAdminReadSerializer(submission).data,
            status=status.HTTP_202_ACCEPTED,
        )


class SurveyTokenViewset(viewsets.GenericViewSet):
    authentication_classes = [SurveyTokenAuthentication]
    permission_classes = [SurveyTokenPermissions]
    queryset = Survey.objects.all()

    def retrieve(self, request, pk):
        survey = self.get_object()
        serialized_survey = SurveyReadDetailedSerializer(survey).data
        serialized_survey["results"] = survey.aggregate_submissions()
        serialized_survey["submissionCount"] = survey.submissions.count()
        return Response(data=serialized_survey)
