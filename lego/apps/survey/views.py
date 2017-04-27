from rest_framework import viewsets

from lego.apps.survey.models import Alternative, Answer, Question, Submission, Survey
from lego.apps.survey.serializers import (AlternativeSerializer, AnswerSerializer,
                                          QuestionSerializer, SubmissionCreateAndUpdateSerializer,
                                          SubmissionReadDetailedSerializer,
                                          SubmissionReadSerializer, SurveyCreateAndUpdateSerializer,
                                          SurveyReadDetailedSerializer, SurveyReadSerializer)


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all().prefetch_related('questions', 'submissions')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SurveyCreateAndUpdateSerializer
        elif self.action in ['retrieve']:
            return SurveyReadDetailedSerializer
        return SurveyReadSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubmissionCreateAndUpdateSerializer
        elif self.action in ['retrieve']:
            return SubmissionReadDetailedSerializer
        return SubmissionReadSerializer

    def get_queryset(self):
        survey_id = self.kwargs.get('survey_pk')
        if survey_id:
            return Submission.objects.filter(survey=survey_id)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AlternativeViewSet(viewsets.ModelViewSet):
    queryset = Alternative.objects.all()
    serializer_class = AlternativeSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
