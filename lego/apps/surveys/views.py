from rest_framework import decorators, exceptions, status, viewsets
from rest_framework.response import Response

from lego.apps.surveys.models import Submission, Survey
from lego.apps.surveys.serializers import (SubmissionCreateAndUpdateSerializer,
                                           SubmissionReadDetailedSerializer,
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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        survey = Survey.objects.get(instance.id)
        survey.delete()


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()

    def get_queryset(self):
        survey_id = self.kwargs['survey_pk']
        return Submission.objects.filter(survey=survey_id)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubmissionCreateAndUpdateSerializer
        elif self.action in ['retrieve']:
            return SubmissionReadDetailedSerializer
        return SubmissionReadSerializer

    @decorators.detail_route(methods=['POST'])
    def submit(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.submitted:
            raise exceptions.ValidationError('Already submitted.')
        instance.submit()
        return Response({'status': 'Received for submission.'},
                        status=status.HTTP_202_ACCEPTED)
