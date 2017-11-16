from rest_framework import viewsets

from lego.apps.surveys.models import Submission, Survey
from lego.apps.surveys.serializers import (SubmissionCreateAndUpdateSerializer,
                                           SubmissionReadSerializer,
                                           SurveyCreateAndUpdateSerializer,
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

    def get_queryset(self):
        survey_id = self.kwargs['survey_pk']
        return Submission.objects.filter(survey=survey_id)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubmissionCreateAndUpdateSerializer
        return SubmissionReadSerializer
