from lego.apps.meetings.serializers import MeetingSerializer, MeetingInvitationSerializer
from rest_framework import viewsets

from lego.apps.meetings.models import Meeting, MeetingInvitation


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()

    def get_serializer_class(self):
        return MeetingSerializer


class MeetingInvitationViewSet(viewsets.ModelViewSet):
    queryset = MeetingInvitation.objects.all()

    def get_serializer_class(self):
        return MeetingInvitationSerializer
