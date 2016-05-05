from rest_framework import viewsets

from lego.apps.bdb.models import Company, SemesterStatus
from lego.apps.bdb.serializers import (CompanyCreateAndUpdateSerializer,
                                       CompanyReadDetailedSerializer, CompanyReadSerializer,
                                       SemesterStatusCreateAndUpdateSerializer,
                                       SemesterStatusReadSerializer)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CompanyCreateAndUpdateSerializer

        company_id = self.kwargs.get('pk', None)
        if company_id:
            return CompanyReadDetailedSerializer

        return CompanyReadSerializer


class SemesterStatusViewSet(viewsets.ModelViewSet):
    queryset = SemesterStatus.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return SemesterStatusCreateAndUpdateSerializer

        return SemesterStatusReadSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk', None)
        if company_id:
            return SemesterStatus.objects.filter(company=company_id)
