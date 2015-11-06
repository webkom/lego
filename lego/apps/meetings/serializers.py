from basis.serializers import BasisSerializer

from lego.apps.meetings.models import Meeting, MeetingInvitation


class MeetingSerializer(BasisSerializer):
    class Meta:
        model = Meeting


class MeetingInvitationSerializer(BasisSerializer):
    class Meta:
        model = MeetingInvitation
        fields = ('id', 'title', 'place', 'date', 'report', 'report_author')
