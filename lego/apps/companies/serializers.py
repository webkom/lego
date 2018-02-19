from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.models import (
    Company, CompanyContact, CompanyFile, CompanyInterest, Semester, SemesterStatus
)
from lego.apps.files.fields import FileField, ImageField
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import User
from lego.utils.serializers import BasisModelSerializer


class SemesterSerializer(BasisModelSerializer):
    class Meta:
        model = Semester
        fields = ('id', 'year', 'semester', 'active_interest_form')


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
    statistics = FileField(required=False, allow_null=True)
    evaluation = FileField(required=False, allow_null=True)

    contract_name = CharField(source='contract_id', read_only=True)
    statistics_name = CharField(source='statistics_id', read_only=True)
    evaluation_name = CharField(source='evaluation_id', read_only=True)

    class Meta:
        model = SemesterStatus
        fields = (
            'id', 'semester', 'contacted_status', 'contract', 'statistics', 'evaluation',
            'contract_name', 'statistics_name', 'evaluation_name'
        )


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
        source='logo', required=False, options={
            'height': 500,
            'width': 500,
            'smart': True
        }
    )

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'description', 'website', 'company_type', 'address', 'logo', 'thumbnail'
        )


class CompanyAdminListSerializer(BasisModelSerializer):
    semester_statuses = SemesterStatusSerializer(many=True, read_only=True)
    student_contact = PublicUserField(required=False, queryset=User.objects.all())

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment', 'active')


class CompanyDetailSerializer(BasisModelSerializer):
    logo = ImageField(required=False, options={'height': 500})

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'description', 'phone', 'company_type', 'website', 'address', 'logo'
        )


class CompanyAdminDetailSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)

    student_contact = PublicUserField(required=False, allow_null=True, queryset=User.objects.all())
    semester_statuses = SemesterStatusDetailSerializer(many=True, read_only=True)
    company_contacts = CompanyContactSerializer(many=True, read_only=True)

    logo = ImageField(required=False, options={'height': 500})
    files = CompanyFileSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'student_contact', 'description', 'phone', 'company_type', 'website',
            'address', 'payment_mail', 'comments', 'comment_target', 'semester_statuses', 'active',
            'admin_comment', 'logo', 'files', 'company_contacts'
        )


class CompanyInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInterest
        fields = (
            'id', 'company_name', 'contact_person', 'mail', 'semesters', 'events', 'other_offers',
            'comment'
        )

    def create(self, validated_data):
        semesters = validated_data.pop('semesters')
        company_interest = CompanyInterest.objects.create(**validated_data)
        company_interest.semesters.add(*semesters)
        company_interest.save()

        return company_interest


class CompanyInterestListSerializer(serializers.ModelSerializer):
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
