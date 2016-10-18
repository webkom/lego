from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.models import Company, CompanyContact, SemesterStatus
from lego.apps.events.models import Event
from lego.apps.users.serializers import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


# SemesterStatus

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
        fields = ('id', 'year', 'semester', 'contacted_status')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        semester_status = SemesterStatus.objects.create(company=company, **validated_data)
        return semester_status


# CompanyContact

class CompanyContactReadSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyContact
        fields = ('id', 'name', 'role', 'mail', 'phone')


class CompanyContactCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = CompanyContact
        fields = ('id', 'name', 'role', 'mail', 'phone')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        company_contact = CompanyContact.objects.create(company=company, **validated_data)
        return company_contact


# Company

class CompanyEventReadSerializer(BasisModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'title', 'event_type', 'start_time')


class CompanyReadSerializer(BasisModelSerializer):
    semester_statuses = SemesterStatusReadSerializer(many=True, read_only=True)
    student_contact = PublicUserSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'active', 'job_offer_only', 'bedex')


class CompanyReadDetailedSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    semester_statuses = SemesterStatusReadDetailedSerializer(many=True, read_only=True)
    student_contact = PublicUserSerializer(read_only=True)
    company_contacts = CompanyContactReadSerializer(many=True, read_only=True)
    events = CompanyEventReadSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'semester_statuses', 'student_contact',
                  'admin_comment', 'website', 'phone', 'address', 'company_contacts',
                  'active', 'job_offer_only', 'bedex', 'events', 'comments', 'comment_target')


class CompanyCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'student_contact', 'admin_comment', 'website',
                  'phone', 'address', 'active', 'job_offer_only', 'bedex')
