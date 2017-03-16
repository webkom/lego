from rest_framework import viewsets

from lego.apps.companies.models import Company, CompanyContact, SemesterStatus
from lego.apps.companies.permissions import CompanyPermissions
from lego.apps.companies.serializers import (CompanyContactCreateAndUpdateSerializer,
                                             CompanyContactReadSerializer,
                                             CompanyCreateAndUpdateSerializer,
                                             CompanyReadDetailedSerializer, CompanyReadSerializer,
                                             SemesterStatusCreateAndUpdateSerializer,
                                             SemesterStatusReadDetailedSerializer,
                                             SemesterStatusReadSerializer)
from lego.apps.permissions.permissions import AbakusPermission


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('semester_statuses', 'student_contact')
    permission_classes = (CompanyPermissions,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyCreateAndUpdateSerializer

        elif self.action in ['retrieve']:
            return CompanyReadDetailedSerializer

        return CompanyReadSerializer


class SemesterStatusViewSet(viewsets.ModelViewSet):
    queryset = SemesterStatus.objects.all()
    permission_classes = (AbakusPermission,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SemesterStatusCreateAndUpdateSerializer

        elif self.action in ['retrieve']:
            return SemesterStatusReadDetailedSerializer

        return SemesterStatusReadSerializer


class CompanyContactViewSet(viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    permission_classes = (AbakusPermission,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyContactCreateAndUpdateSerializer

        return CompanyContactReadSerializer
