from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.models import (Company, CompanyContact, CompanyInterest, Semester,
                                        SemesterStatus)
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class SemesterSerializer(BasisModelSerializer):
    class Meta:
        model = Semester
        fields = ('id', 'year', 'semester')


class SemesterStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = SemesterStatus
        fields = ('id', 'semester', 'contacted_status')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        validated_data['company'] = company
        return super().create(validated_data)


class CompanyContactSerializer(BasisModelSerializer):

    class Meta:
        model = CompanyContact
        fields = ('id', 'name', 'role', 'mail', 'phone', 'mobile')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        validated_data['company'] = company
        return super().create(validated_data)


class CompanyListSerializer(BasisModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'website', 'company_type', 'address')


class CompanyAdminListSerializer(BasisModelSerializer):
    semester_statuses = SemesterStatusSerializer(many=True, read_only=True)
    student_contact = PublicUserSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'active')


class CompanyDetailSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    student_contact = PublicUserField(queryset=User.objects.all())

    class Meta:
        model = Company
        fields = ('id', 'name', 'student_contact', 'description', 'phone',
                  'company_type', 'website', 'address', 'payment_mail', 'comments',
                  'comment_target')


class CompanyAdminDetailSerializer(BasisModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'website', 'company_type', 'address')


class CompanyEditSerializer(BasisModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'name', 'student_contact', 'previous_contacts', 'description', 'phone',
                  'company_type', 'website', 'address', 'payment_mail')


class CompanyInterestSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyInterest
        fields = ('id', 'company_name', 'contact_person', 'mail', 'semesters', 'events',
                  'read_me', 'collaboration', 'itdagene', 'comment')


class CompanyInterestListSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyInterest
        fields = ('id', 'company_name', 'contact_person', 'mail')


class CompanySearchSerializer(serializers.ModelSerializer):
    """
    Public company information available on search.
    """
    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'website', 'company_type', 'address')
