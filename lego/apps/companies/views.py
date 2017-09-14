from rest_framework import viewsets

from lego.apps.companies.models import (Company, CompanyContact, CompanyInterest, Semester,
                                        SemesterStatus)
from lego.apps.companies.serializers import (CompanyAdminDetailSerializer,
                                             CompanyAdminListSerializer, CompanyContactSerializer,
                                             CompanyDetailSerializer, CompanyInterestListSerializer,
                                             CompanyInterestSerializer, CompanyListSerializer,
                                             SemesterSerializer, SemesterStatusSerializer)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.constants import EDIT


class CompanyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('semester_statuses')\
        .select_related('student_contact')

    def get_serializer_class(self):
        if not self.request:
            return CompanyDetailSerializer

        user = self.request.user
        is_admin = user.has_perm(EDIT, self.get_queryset())

        if self.action == 'list':
            return CompanyAdminListSerializer if is_admin else CompanyListSerializer

        return CompanyAdminDetailSerializer if is_admin else CompanyDetailSerializer


class SemesterStatusViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = SemesterStatus.objects.all()
    serializer_class = SemesterStatusSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return SemesterStatus.objects.filter(company=company_id)


class CompanyContactViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return CompanyContact.objects.filter(company=company_id)


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer


class CompanyInterestViewSet(viewsets.ModelViewSet):
    """
    Used by new companies to register interest in Abakus and our services.
    """
    queryset = CompanyInterest.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyInterestListSerializer
        return CompanyInterestSerializer
