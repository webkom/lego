from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.surveys.filters import SubmissionFilterSet
from lego.apps.surveys.models import Submission, Survey
from lego.apps.surveys.permissions import SubmissionPermissions, SurveyPermissions
from lego.apps.surveys.serializers import (
    SubmissionCreateAndUpdateSerializer, SubmissionReadSerializer, SurveyCreateSerializer,
    SurveyReadDetailedSerializer, SurveyReadSerializer, SurveyUpdateSerializer
)


class SurveyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Survey.objects.all().prefetch_related('questions', 'submissions'
                                                     ).exclude(template_type__isnull=False)
    permission_classes = [SurveyPermissions]
    serializer_class = SurveyReadSerializer

    def get_serializer_class(self):
        if self.action in ['create']:
            return SurveyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SurveyUpdateSerializer
        elif self.action in ['retrieve']:
            return SurveyReadDetailedSerializer

        return super().get_serializer_class()


class SurveyTemplateViewSet(SurveyViewSet):
    queryset = Survey.objects.all().prefetch_related('questions').filter(template_type__isnull=False)

    def get_queryset(self):
        if self.action in ['retrieve']:
            queryset = self.queryset
            print('template detail', self.queryset, 'asd', self.kwargs)
            template_type = self.kwargs['pk']
            return queryset.get(template_type=template_type)


class SubmissionViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    permission_classes = [SubmissionPermissions]
    filter_class = SubmissionFilterSet

    def get_queryset(self):
        survey_id = self.kwargs['survey_pk']
        return Submission.objects.filter(survey=survey_id)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SubmissionCreateAndUpdateSerializer
        return SubmissionReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            SubmissionReadSerializer(serializer.instance).data, status=status.HTTP_201_CREATED
        )
