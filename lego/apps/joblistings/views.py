from django.utils import timezone
from rest_framework import viewsets

from lego.apps.joblistings.models import Joblisting
from lego.apps.joblistings.serializer import (JoblistingCreateAndUpdateSerializer,
                                              JoblistingDetailedSerializer, JoblistingSerializer)
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class JoblistingViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    pagination_class = None

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
