from basis.serializers import BasisSerializer

from lego.apps.meetings.models import Meeting, MeetingInvitation


class MeetingSerializer(BasisSerializer):
    class Meta:
        model = Meeting
        fields = ('id', 'title', 'location', 'start_time', 'end_time', 'report', 'report_author')


class MeetingInvitationSerializer(BasisSerializer):
    class Meta:
        model = MeetingInvitation
        fields = ('meeting', 'status')
