from django.utils import timezone
from rest_framework import viewsets, decorators
from rest_framework.response import Response

from lego.apps.admissions.models import Admission, Application, Committee
from lego.apps.admissions.serializers import ApplicationSerializer, CommitteeSerializer, AdmissionSerializer
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class AdmissionViewSet(viewsets.ModelViewSet):

    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer

    @decorators.list_route(
        methods=['GET'], serializer_class=AdmissionSerializer
    )
    def current(self, request):
        instance = self.get_queryset().filter(
            application_deadline__gt=timezone.now()
        ).first()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

class ApplicationViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class CommitteeViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer