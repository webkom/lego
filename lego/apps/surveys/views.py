import csv

from django.http import HttpResponse
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

    @action(detail=True, methods=["GET"])
    def csv(self, *args, **kwargs):
        user = self.request.user
        is_admin = user.has_perm(EDIT, obj=Survey)
        if not is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)

        def describe_results(survey):
            choice_answers = []
            text_answers = []
            submissions = Submission.objects.filter(survey=survey)
            for question in survey.questions.all():
                if question.question_type != TEXT_FIELD:
                    answers = []
                    answers.append(["question", question.question_text])
                    answers.append(["value:", "count:"])
                    for option in question.options.all():
                        number_of_selections = submissions.filter(
                            answers__selected_options__in=[option.id]
                        ).count()
                        answers.append([option.option_text, number_of_selections])
                    choice_answers.append(answers)
                else:
                    answers = []
                    answers.append([question.question_text])
                    answers.append(["answer:"])
                    answers += [
                        [answer.answer_text]
                        for answer in Answer.objects.filter(question=question).exclude(
                            hide_from_public=True
                        )
                    ]
                    text_answers.append(answers)
            return choice_answers + text_answers

        survey = Survey.objects.get(pk=kwargs["pk"])

        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{survey.title.replace(" ", "_")}.csv"'

        writer = csv.writer(response)
        for question in describe_results(survey):
            for line in question:
                writer.writerow(line)
            writer.writerow([])

        return response


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
        print("###", request)
        user = request.user.id
        print("%%%", user)
        survey = Survey.objects.get(pk=kwargs["survey_pk"])
        user_has_already_answered = user in survey.answered_by
        print("user_has_already_answered", user_has_already_answered)
        if user_has_already_answered:
            return Response(
                data='You have already anwered this survey.',
                status=status.HTTP_409_CONFLICT,
            )

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
