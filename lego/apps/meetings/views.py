from rest_framework import viewsets

from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.meetings.permissions import MeetingInvitationPermissions, MeetingPermissions
from lego.apps.meetings.serializers import MeetingInvitationSerializer, MeetingSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    permission_classes = (MeetingPermissions,)

    def get_serializer_class(self):
        return MeetingSerializer


class MeetingInvitationViewSet(viewsets.ModelViewSet):
    queryset = MeetingInvitation.objects.all()
    permission_classes = (MeetingInvitationPermissions,)

    def get_serializer_class(self):
        return MeetingInvitationSerializer
