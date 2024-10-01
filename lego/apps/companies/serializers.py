from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.constants import INTERESTED, NOT_CONTACTED
from lego.apps.companies.models import (
    Company,
    CompanyContact,
    CompanyFile,
    CompanyInterest,
    Semester,
    SemesterStatus,
    StudentCompanyContact
)
from lego.apps.files.fields import FileField, ImageField
from lego.apps.users.fields import PublicUserField
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.apps.users.models import User
from lego.utils.serializers import BasisModelSerializer


class SemesterSerializer(BasisModelSerializer):
    class Meta:
        model = Semester
        fields = ("id", "year", "semester", "active_interest_form")


class SemesterStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterStatus
        fields = ("id", "semester", "contacted_status")

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context["view"].kwargs["company_pk"])
        validated_data["company"] = company
        return super().create(validated_data)


class SemesterStatusDetailSerializer(SemesterStatusSerializer):
    contract = FileField(required=False, allow_null=True)
    statistics = FileField(required=False, allow_null=True)
    evaluation = FileField(required=False, allow_null=True)

    contract_name = CharField(source="contract_id", read_only=True)
    statistics_name = CharField(source="statistics_id", read_only=True)
    evaluation_name = CharField(source="evaluation_id", read_only=True)

    class Meta:
        model = SemesterStatus
        fields = (
            "id",
            "semester",
            "contacted_status",
            "contract",
            "statistics",
            "evaluation",
            "contract_name",
            "statistics_name",
            "evaluation_name",
        )


class CompanyContactSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyContact
        fields = ("id", "name", "role", "mail", "phone", "mobile")

    def create(self, validated_data) -> any:
        company = Company.objects.get(pk=self.context["view"].kwargs["company_pk"])
        validated_data["company"] = company
        return super().create(validated_data)


class CompanyFileSerializer(serializers.ModelSerializer):
    file = FileField()

    class Meta:
        model = CompanyFile
        fields = ("id", "file")

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context["view"].kwargs["company_pk"])
        validated_data["company"] = company
        return super().create(validated_data)


class CompanyListSerializer(BasisModelSerializer):
    logo = ImageField(required=False, options={"height": 500})
    logo_placeholder = ImageField(
        source="logo", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )
    thumbnail = ImageField(
        source="logo",
        required=False,
        options={
            "fit_in": True,
            "height": 500,
            "width": 500,
            "filters": ["fill(white)"],
        },
    )

    event_count = serializers.SerializerMethodField()
    joblisting_count = serializers.SerializerMethodField()

    def get_event_count(self, obj):
        return obj.events.filter(start_time__gt=timezone.now()).count()

    def get_joblisting_count(self, obj):
        return obj.joblistings.filter(visible_to__gte=timezone.now()).count()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "description",
            "event_count",
            "joblisting_count",
            "website",
            "company_type",
            "address",
            "logo",
            "logo_placeholder",
            "thumbnail",
            "active",
        )


class CompanyAdminListSerializer(BasisModelSerializer):
    semester_statuses = serializers.SerializerMethodField()
    student_contact = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "semester_statuses",
            "student_contact",
            "admin_comment",
            "active",
        )

    def get_student_contact(self, obj):
        semester_id = self.context.get('semester_id')
        student_company_contact = StudentCompanyContact.objects.filter(company=obj, semester_id=semester_id).first()
        return PublicUserSerializer(student_company_contact.student_contact).data if student_company_contact else None

    def get_semester_statuses(self, obj):
        semester_id = self.context.get('semester_id')
        semester_statuses = SemesterStatus.objects.filter(company=obj, semester_id=semester_id)
        return SemesterStatusSerializer(semester_statuses, many=True).data



class CompanyDetailSerializer(BasisModelSerializer):
    logo = ImageField(required=False, options={"height": 500})
    logo_placeholder = ImageField(
        source="logo", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "description",
            "phone",
            "company_type",
            "website",
            "address",
            "logo",
            "logo_placeholder",
        )


class CompanySearchSerializer(serializers.ModelSerializer):
    """
    Public company information available on search.
    """

    class Meta:
        model = Company
        fields = ("id", "name", "description", "website", "company_type", "address")


class CompanyAdminDetailSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    content_target = CharField(read_only=True)

    student_contact = PublicUserField(
        required=False, allow_null=True, queryset=User.objects.all()
    )
    semester_statuses = SemesterStatusDetailSerializer(many=True, read_only=True)
    company_contacts = CompanyContactSerializer(many=True, read_only=True)

    logo = ImageField(required=False, options={"height": 500})
    files = CompanyFileSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "student_contact",
            "description",
            "phone",
            "company_type",
            "website",
            "address",
            "payment_mail",
            "comments",
            "content_target",
            "semester_statuses",
            "active",
            "admin_comment",
            "logo",
            "files",
            "company_contacts",
        )


class CompanyInterestCreateAndUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInterest
        fields = (
            "id",
            "company_name",
            "company",
            "contact_person",
            "mail",
            "phone",
            "semesters",
            "events",
            "other_offers",
            "collaborations",
            "company_type",
            "target_grades",
            "participant_range_start",
            "participant_range_end",
            "comment",
            "course_comment",
            "breakfast_talk_comment",
            "other_event_comment",
            "startup_comment",
            "company_to_company_comment",
            "lunch_presentation_comment",
            "company_presentation_comment",
            "bedex_comment",
            "company_course_themes",
            "office_in_trondheim",
        )

    def update_company_interest_bdb(self, company_interest):
        company = company_interest.company
        for semester in company_interest.semesters.all():
            if company:
                semester_status, created = SemesterStatus.objects.get_or_create(
                    semester=semester,
                    company=company,
                    defaults={"contacted_status": []},
                )
                if len(semester_status.contacted_status) == 0:
                    semester_status.contacted_status.append(INTERESTED)
                elif semester_status.contacted_status[0] == NOT_CONTACTED:
                    semester_status.contacted_status[0] = INTERESTED
                semester_status.save()

    def create(self, validated_data):
        with transaction.atomic():
            semesters = validated_data.pop("semesters")
            company_interest = CompanyInterest.objects.create(**validated_data)
            company_interest.semesters.add(*semesters)
            company_interest.save()
            self.update_company_interest_bdb(company_interest)
            return company_interest

    def update(self, instance, validated_data):
        with transaction.atomic():
            semesters = validated_data.pop("semesters")
            updated_instance = super().update(instance, validated_data)
            updated_instance.semesters.add(*semesters)
            updated_instance.save()
            self.update_company_interest_bdb(updated_instance)
            return updated_instance


class CompanyInterestSerializer(CompanyInterestCreateAndUpdateSerializer):
    company = CompanySearchSerializer(many=False, read_only=False, allow_null=True)


class CompanyInterestListSerializer(serializers.ModelSerializer):
    company = CompanySearchSerializer(many=False)

    class Meta:
        model = CompanyInterest
        fields = (
            "id",
            "company_name",
            "company",
            "contact_person",
            "mail",
            "phone",
            "semesters",
            "events",
            "created_at",
        )
