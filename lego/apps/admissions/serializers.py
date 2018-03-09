from rest_framework import serializers

from lego.apps.admissions.models import Admission, Application, CommitteeApplication, Committee
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer

class CommitteeSerializer(BasisModelSerializer):
    group = PublicAbakusGroupSerializer()

    class Meta:
        model = Committee
        fields = ('id', 'group', 'name', 'description', 'response_label')

class CommitteeApplicationSerializer(serializers.ModelSerializer):
    committee = CommitteeSerializer()

    class Meta:
        model = CommitteeApplication
        fields = ('id', 'committee', 'priority', 'text')


class ApplicationSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer()
    committee_applications = CommitteeApplicationSerializer(many=True)

    class Meta:
        model = Application
        fields = ('id', 'user', 'text', 'time_sent', 'committee_applications')


class AdmissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Admission
        fields = (
            'id', 'title', 'open_from', 'public_deadline', 'application_deadline', 'is_closed', 'is_appliable'
        )
