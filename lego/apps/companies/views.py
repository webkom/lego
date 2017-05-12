from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from lego.apps.companies.models import Company, CompanyContact, CompanyInterest, SemesterStatus
from lego.apps.companies.permissions import CompanyPermissions
from lego.apps.companies.serializers import (CompanyContactCreateAndUpdateSerializer,
                                             CompanyContactReadSerializer,
                                             CompanyCreateAndUpdateSerializer,
                                             CompanyInterestCreateSerializer,
                                             CompanyInterestListSerializer,
                                             CompanyInterestReadDetailedSerializer,
                                             CompanyReadDetailedSerializer, CompanyReadSerializer,
                                             SemesterCreateSerializer,
                                             SemesterStatusCreateAndUpdateSerializer,
                                             SemesterStatusReadDetailedSerializer,
                                             SemesterStatusReadSerializer)
from lego.apps.permissions.views import AllowedPermissionsMixin


class CompanyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('semester_statuses', 'student_contact')
    permission_classes = (CompanyPermissions,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyCreateAndUpdateSerializer

        elif self.action in ['retrieve']:
            return CompanyReadDetailedSerializer

        return CompanyReadSerializer


class SemesterStatusViewSet(AllowedPermissionsMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    queryset = SemesterStatus.objects.all()
    permission_classes = (CompanyPermissions,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SemesterStatusCreateAndUpdateSerializer

        elif self.action in ['retrieve']:
            return SemesterStatusReadDetailedSerializer

        return SemesterStatusReadSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk')
        if company_id:
            return SemesterStatus.objects.filter(company=company_id)


class CompanyContactViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    permission_classes = (CompanyPermissions,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyContactCreateAndUpdateSerializer

        return CompanyContactReadSerializer

    def get_queryset(self):
        company_id = self.kwargs.get('company_pk')
        if company_id:
            return CompanyContact.objects.filter(company=company_id)


class CompanyInterestViewSet(viewsets.ModelViewSet):
    queryset = CompanyInterest.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CompanyInterestCreateSerializer
        elif self.action in ['retrieve', 'destroy']:
            return CompanyInterestReadDetailedSerializer

        return CompanyInterestListSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = CompanyInterest.objects.all()

    def get_serializer_class(self):
        return SemesterCreateSerializer

    def get_queryset(self):
        if self.action in ['retrieve', 'destroy']:
            semester_id = self.kwargs.get('semester_pk', None)
            return CompanyInterest.objects.filter(semester=semester_id)
        return self.queryset
