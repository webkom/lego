from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.models import (Company, CompanyContact, CompanyFile, CompanyInterest,
                                        Semester, SemesterStatus)
from lego.apps.files.fields import FileField, ImageField
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
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


class SemesterStatusDetailSerializer(SemesterStatusSerializer):
    contract = FileField(required=False, allow_null=True)

    class Meta:
        model = SemesterStatus
        fields = ('id', 'semester', 'contacted_status', 'contract')


class CompanyContactSerializer(BasisModelSerializer):

    class Meta:
        model = CompanyContact
        fields = ('id', 'name', 'role', 'mail', 'phone', 'mobile')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        validated_data['company'] = company
        return super().create(validated_data)


class CompanyFileSerializer(serializers.ModelSerializer):
    file = FileField()

    class Meta:
        model = CompanyFile
        fields = ('id', 'file')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        validated_data['company'] = company
        return super().create(validated_data)


class CompanyListSerializer(BasisModelSerializer):
    logo = ImageField(required=False, options={'height': 500})
    thumbnail = ImageField(
        source='logo',
        required=False,
        options={'height': 500, 'width': 500, 'smart': True}
    )

    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'website', 'company_type', 'address', 'logo', 'thumbnail')


class CompanyAdminListSerializer(BasisModelSerializer):
    semester_statuses = SemesterStatusSerializer(many=True, read_only=True)
    student_contact = PublicUserField(required=False, queryset=User.objects.all())

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'active')


class CompanyDetailSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    student_contact = PublicUserField(required=False, queryset=User.objects.all())

    logo = ImageField(required=False, options={'height': 500})

    class Meta:
        model = Company
        fields = ('id', 'name', 'student_contact', 'description', 'phone',
                  'company_type', 'website', 'address', 'payment_mail', 'comments',
                  'comment_target', 'logo')


class CompanyAdminDetailSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    student_contact = PublicUserField(required=False, allow_null=True, queryset=User.objects.all())
    semester_statuses = SemesterStatusDetailSerializer(many=True, read_only=True)

    logo = ImageField(required=False, options={'height': 500})
    files = CompanyFileSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'student_contact', 'description', 'phone',
                  'company_type', 'website', 'address', 'payment_mail', 'comments',
                  'comment_target', 'semester_statuses', 'active', 'admin_comment',
                  'logo', 'files')


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
