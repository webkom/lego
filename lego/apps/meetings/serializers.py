from rest_framework import serializers
from rest_framework_jwt.serializers import User

from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class MeetingInvitationSerializer(BasisModelSerializer):
    user = PublicUserSerializer()

    class Meta:
        model = MeetingInvitation
        fields = ('user', 'status')

    def create(self, validated_data):
        meeting = Meeting.objects.get(id=self.context['view'].kwargs['meeting_pk'])
        meeting_invitation = MeetingInvitation.objects.create(meeting=meeting,
                                                              **validated_data)
        return meeting_invitation


class MeetingInvitationUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = MeetingInvitation
        fields = ('status',)


class MeetingGroupInvite(serializers.Serializer):
    group = PrimaryKeyRelatedFieldNoPKOpt(queryset=AbakusGroup.objects.all())


class MeetingUserInvite(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())


class MeetingSerializer(BasisModelSerializer):
    invitations = MeetingInvitationSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ('id', 'created_by', 'title', 'location', 'start_time', 'end_time', 'report',
                  'report_author', 'invitations')

    def create(self, validated_data):
        meeting = Meeting.objects.create(**validated_data)
        owner = self.context['request'].user
        meeting.invite_user(owner)
        return meeting
