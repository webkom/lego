from rest_framework.fields import CharField

from lego.apps.bdb.models import Company, SemesterStatus
from lego.apps.comments.serializers import CommentSerializer
from lego.apps.users.serializers import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class SemesterStatusReadSerializer(BasisModelSerializer):
    class Meta:
        model = SemesterStatus
        fields = ('id', 'year', 'semester', 'contacted_status')


class SemesterStatusCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = SemesterStatus
        fields = ('id', 'year', 'semester', 'contacted_status')

    def create(self, validated_data):
        company = Company.objects.get(pk=self.context['view'].kwargs['company_pk'])
        semester_status = SemesterStatus.objects.create(company=company, **validated_data)
        return semester_status


class CompanyReadSerializer(BasisModelSerializer):
    semester_statuses = SemesterStatusReadSerializer(many=True, read_only=True)
    student_contact = PublicUserSerializer(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'job_offer_only')


class CompanyReadDetailedSerializer(BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    semester_statuses = SemesterStatusReadSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'semester_statuses', 'student_contact', 'admin_comment',
                  'job_offer_only', 'phone', 'comments', 'comment_target')


class CompanyCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'name', 'student_contact', 'admin_comment', 'job_offer_only', 'phone')
