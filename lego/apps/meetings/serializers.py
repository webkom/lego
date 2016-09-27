from basis.serializers import BasisSerializer

from lego.apps.meetings.models import Meeting, MeetingInvitation


class MeetingSerializer(BasisSerializer):
    class Meta:
        model = Meeting
        fields = ('id', 'title', 'location', 'author', 'start_time', 'end_time', 'report',
                  'report_author')

    def create(self, validated_data):
        meeting = Meeting.objects.create(**validated_data)
        owner = self.context['request'].user
        meeting.invite(owner)
        return meeting


class MeetingInvitationSerializer(BasisSerializer):
    class Meta:
        model = MeetingInvitation
        fields = ('user', 'status')

    def create(self, validated_data):
        meeting = Meeting.objects.get(id=self.context['view'].kwargs['meeting_pk'])
        meeting_invitation = MeetingInvitation.objects.create(meeting=meeting,
                                                              **validated_data)
        return meeting_invitation
