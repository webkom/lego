from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.constants import INTERESTED, NOT_CONTACTED
from lego.apps.companies.fields import SemesterField
from lego.apps.companies.models import (
    Company,
    CompanyContact,
    CompanyFile,
    CompanyInterest,
    Semester,
    SemesterStatus,
    StudentCompanyContact,
)
from lego.apps.files.fields import FileField, ImageField
from lego.apps.users.fields import PublicUserField
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


class StudentCompanyContactSerializer(BasisModelSerializer):
    user = PublicUserField(queryset=User.objects.all())
    semester = SemesterField(queryset=Semester.objects.all())

    class Meta:
        model = StudentCompanyContact
        fields = ("id", "company", "user", "semester")


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
        fields = ("id", "name", "role", "mail", "phone", "mobile", "updated_at")

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
    student_contacts = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "semester_statuses",
            "student_contacts",
            "active",
        )

    def get_student_contacts(self, obj):
        semester_id = self.context.get("semester_id")

        if semester_id is None:
            queryset = StudentCompanyContact.objects.filter(company=obj)
        else:
            queryset = StudentCompanyContact.objects.filter(
                company=obj, semester_id=semester_id
            )

        return StudentCompanyContactSerializer(queryset, many=True).data

    def get_semester_statuses(self, obj):
        semester_id = self.context.get("semester_id")

        if semester_id is None:
            queryset = SemesterStatus.objects.filter(company=obj)
        else:
            queryset = SemesterStatus.objects.filter(
                company=obj, semester_id=semester_id
            )

        return SemesterStatusSerializer(queryset, many=True).data


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

    student_contacts = StudentCompanyContactSerializer(many=True, required=False)
    semester_statuses = SemesterStatusDetailSerializer(many=True, read_only=True)
    company_contacts = CompanyContactSerializer(many=True, read_only=True)

    logo = ImageField(required=False, options={"height": 500})
    files = CompanyFileSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "student_contacts",
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
            "logo",
            "files",
            "company_contacts",
        )

    def update(self, instance, validated_data):
        updated_student_contacts = validated_data.pop("student_contacts", [])

        previous_student_contacts = list(instance.student_contacts.all())
        previous_ids = {contact.id for contact in previous_student_contacts}

        existing_contacts_ids = set()

        for student_contact in updated_student_contacts:
            try:
                existing_contact = StudentCompanyContact.objects.get(
                    company=student_contact.get("company"),
                    semester=student_contact.get("semester"),
                    user=student_contact.get("user"),
                )
                existing_contacts_ids.add(existing_contact.id)
            except StudentCompanyContact.DoesNotExist:
                StudentCompanyContact(
                    company=student_contact.get("company"),
                    semester=student_contact.get("semester"),
                    user=student_contact.get("user"),
                ).save()

        delete_contacts_ids = previous_ids.difference(existing_contacts_ids)
        for contact_id in delete_contacts_ids:
            StudentCompanyContact.objects.get(id=contact_id).delete()

        return super().update(instance, validated_data)


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
            "wants_thursday_event",
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
