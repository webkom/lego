from rest_framework import serializers

from lego.apps.meetings import constants
from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.users.fields import PublicUserField
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class MeetingInvitationSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    status = serializers.ChoiceField(choices=(constants.ATTENDING,
                                              constants.NOT_ATTENDING))

    class Meta:
        model = MeetingInvitation
        fields = ('user', 'status', 'meeting')

    def create(self, validated_data):
        meeting = Meeting.objects.get(
            id=self.context['view'].kwargs['meeting_pk'])
        meeting_invitation = MeetingInvitation.objects.create(
            meeting=meeting, **validated_data)
        return meeting_invitation


class MeetingInvitationUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = MeetingInvitation
        fields = ('status', )


class MeetingGroupInvite(serializers.Serializer):
    group = PrimaryKeyRelatedFieldNoPKOpt(queryset=AbakusGroup.objects.all())


class MeetingUserInvite(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())


class MeetingBulkInvite(serializers.Serializer):
    users = PrimaryKeyRelatedFieldNoPKOpt(
        queryset=User.objects.all(), many=True, required=False)
    groups = PrimaryKeyRelatedFieldNoPKOpt(
        queryset=AbakusGroup.objects.all(), many=True, required=False)


class MeetingSerializer(BasisModelSerializer):
    invitations = MeetingInvitationSerializer(many=True, read_only=True)
    report_author = PublicUserField(
        queryset=User.objects.all(), allow_null=True, required=False)
    created_by = PublicUserField(read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'created_by', 'title', 'location', 'start_time',
                  'end_time', 'report', 'report_author', 'invitations')

    def create(self, validated_data):
        meeting = Meeting.objects.create(**validated_data)
        owner = validated_data['current_user']
        meeting.invite_user(owner, owner)
        return meeting
