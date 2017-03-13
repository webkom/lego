from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.models import (Company, CompanyContact, CompanyInterest, Semester,
                                        SemesterStatus)
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class SemesterStatusReadSerializer(BasisModelSerializer):
    class Meta:
        model = SemesterStatus
        fields = ('id', 'year', 'semester', 'contacted_status')


class SemesterStatusReadDetailedSerializer(BasisModelSerializer):
    class Meta:
        model = SemesterStatus
        fields = ('id', 'year', 'semester', 'contacted_status', 'contract')


class SemesterStatusCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = SemesterStatus
        fields = ('id', 'year', 'semester', 'contacted_status', 'contract')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        semester_status = SemesterStatus.objects.create(company=company, **validated_data)
        return semester_status


# CompanyContact

class CompanyContactReadSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyContact
        fields = ('id', 'name', 'role', 'mail', 'phone', 'mobile')


class CompanyContactCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyContact
        fields = ('id', 'name', 'role', 'mail', 'phone', 'mobile')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        company_contact = CompanyContact.objects.create(company=company, **validated_data)
        return company_contact


# Company

class PublicCompanyReadSerializer(BasisModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'website')


class CompanyReadSerializer(BasisModelSerializer):
    semester_statuses = SemesterStatusReadSerializer(many=True, read_only=True)
    student_contact = PublicUserSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'active')


class CompanyReadDetailedSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    semester_statuses = SemesterStatusReadDetailedSerializer(many=True, read_only=True)
    student_contact = PublicUserSerializer(read_only=True)
    company_contacts = CompanyContactReadSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'description', 'website', 'phone', 'company_type', 'address', 'payment_mail',
                  'company_contacts', 'active', 'comments', 'comment_target')


class CompanyCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'student_contact', 'admin_comment', 'website',
                  'phone', 'address', 'active')


class CompanySearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'student_contact', 'admin_comment', 'description',
                  'website', 'phone', 'company_type', 'address', 'payment_mail', 'active')

# Semester


class SemesterCreateSerializer(BasisModelSerializer):
    class Meta:
        model = Semester
        fields = ('id', 'year', 'spring')
        """
        def create(self, validated_data):
            semester = Semester.objects.get(pk=self.context['view'].kwargs['semester_pk'])
            semester = Semester.objects.create(semester=semester, **validated_data)
            return semester
        """


# CompanyInterest


class CompanyInterestCreateSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyInterest
        fields = ('id', 'company_name', 'contact_person', 'mail', 'semesters', 'events',
                  'readMe', 'collaboration', 'itdagene', 'comment')


class CompanyInterestReadDetailedSerializer(BasisModelSerializer):
    semesters = SemesterCreateSerializer(read_only=True, many=True)

    class Meta:
        model = CompanyInterest
        fields = ('id', 'company_name', 'contact_person', 'mail', 'semesters', 'events',
                  'readMe', 'collaboration', 'itdagene', 'comment')


class CompanyInterestListSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyInterest
        fields = ('id', 'company_name', 'contact_person', 'mail')
