from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from lego.apps.survey.models import Survey, Submission, Question, Alternative, Answer
from lego.apps.survey.serializers import SurveyReadSerializer


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveyReadSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()


class AlternativeViewSet(viewsets.ModelViewSet):
    queryset = Alternative.objects.all()


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()




