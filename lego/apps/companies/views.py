from rest_framework import permissions, viewsets

from lego.apps.companies.filters import CompanyInterestFilterSet, SemesterFilterSet
from lego.apps.companies.models import (
    Company, CompanyContact, CompanyFile, CompanyInterest, Semester, SemesterStatus
)
from lego.apps.companies.serializers import (
    CompanyAdminDetailSerializer, CompanyAdminListSerializer, CompanyContactSerializer,
    CompanyDetailSerializer, CompanyFileSerializer, CompanyInterestListSerializer,
    CompanyInterestSerializer, CompanyListSerializer, SemesterSerializer,
    SemesterStatusDetailSerializer, SemesterStatusSerializer
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin


class AdminCompanyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('semester_statuses', 'files')\
        .select_related('student_contact')
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyAdminListSerializer

        return CompanyAdminDetailSerializer


class CompanyViewSet(
    AllowedPermissionsMixin, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Company.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer

        return CompanyDetailSerializer


class CompanyFilesViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyFile.objects.all()
    serializer_class = CompanyFileSerializer
    ordering = 'id'

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return CompanyFile.objects.filter(company=company_id)


class SemesterStatusViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = SemesterStatus.objects.all()
    serializer_class = SemesterStatusDetailSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return SemesterStatus.objects.filter(company=company_id)

    def get_serializer_class(self):
        if self.action == 'list':
            return SemesterStatusSerializer

        return super().get_serializer_class()


class CompanyContactViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return CompanyContact.objects.filter(company=company_id)


class SemesterViewSet(viewsets.ModelViewSet):
    filter_class = SemesterFilterSet

    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    pagination_class = None


class CompanyInterestViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    """
    Used by new companies to register interest in Abakus and our services.
    """
    ordering = '-created_at'
    queryset = CompanyInterest.objects.all()
    filter_class = CompanyInterestFilterSet

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyInterestListSerializer
        return CompanyInterestSerializer
