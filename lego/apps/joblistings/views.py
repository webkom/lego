from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from lego.apps.joblistings.models import Joblisting
from lego.apps.joblistings.serializer import (JoblistingCreateAndUpdateSerializer,
                                              JoblistingDetailedSerializer, JoblistingSerializer)


class JoblistingViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JoblistingCreateAndUpdateSerializer

        elif self.action in ['retrieve', 'destroy']:
            return JoblistingDetailedSerializer

        return JoblistingSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Joblisting.objects.filter(visible_from__lte=timezone.now(),
                                             visible_to__gte=timezone.now())
        return Joblisting.objects.all()
