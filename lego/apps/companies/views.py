from rest_framework import viewsets

from lego.apps.companies.models import Company, CompanyContact, SemesterStatus
from lego.apps.companies.serializers import (CompanyContactCreateAndUpdateSerializer,
                                             CompanyContactReadSerializer,
                                             CompanyCreateAndUpdateSerializer,
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
        if self.action in ['create', 'update', 'partial_update']:
            return SemesterStatusCreateAndUpdateSerializer

        return SemesterStatusReadSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk', None)
        if company_id:
            return SemesterStatus.objects.filter(company=company_id)


class CompanyContactViewSet(viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return CompanyContactCreateAndUpdateSerializer

        return CompanyContactReadSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk', None)
        if company_id:
            return CompanyContact.objects.filter(company=company_id)
