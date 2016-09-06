from rest_framework import viewsets

from lego.apps.joblistings.models import Joblisting
from lego.apps.joblistings.serializer import (JoblistingSerializer,
                                              JoblistingDetailedSerializer,
                                              JoblistingCreateAndUpdateSerializer)


class JoblistingViewSet(viewsets.ModelViewSet):
    queryset = Joblisting.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JoblistingCreateAndUpdateSerializer

        elif self.action in ['retrieve', 'destroy']:
            return JoblistingDetailedSerializer

        return JoblistingSerializer
