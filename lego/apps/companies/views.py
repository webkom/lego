from rest_framework import viewsets

from lego.apps.companies.models import (Company, CompanyContact, CompanyInterest, Semester,
                                        SemesterStatus)
from lego.apps.companies.permissions import CompanyInterestPermissions, CompanyPermissions
from lego.apps.companies.serializers import (CompanyContactSerializer, CompanyDetailSerializer,
                                             CompanyInterestListSerializer,
                                             CompanyInterestSerializer, CompanyListSerializer,
                                             SemesterSerializer, SemesterStatusSerializer)
from lego.apps.permissions.views import AllowedPermissionsMixin


class CompanyViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all().prefetch_related('semester_statuses', 'student_contact')
    permission_classes = (CompanyPermissions, )

    def get_serializer_class(self):
        """
        TODO: Public detail serializer.
        """
        if self.action == 'list':
            return CompanyListSerializer
        return CompanyDetailSerializer


class SemesterStatusViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = SemesterStatus.objects.all()
    serializer_class = SemesterStatusSerializer
    permission_classes = (CompanyPermissions,)

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return SemesterStatus.objects.filter(company=company_id)


class CompanyContactViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer
    permission_classes = (CompanyPermissions,)

    def get_queryset(self):
        company_id = self.kwargs['company_pk']
        return CompanyContact.objects.filter(company=company_id)


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = (CompanyPermissions,)


class CompanyInterestViewSet(viewsets.ModelViewSet):
    """
    Used by new companies to register interest in Abakus and our services.
    """
    queryset = CompanyInterest.objects.all()
    permission_classes = (CompanyInterestPermissions, )

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyInterestListSerializer
        return CompanyInterestSerializer
