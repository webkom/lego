from rest_framework import decorators, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.meetings.permissions import (MeetingIntitationTokenPermission,
                                            MeetingInvitationPermissions, MeetingPermissions)
from lego.apps.meetings.serializers import (MeetingBulkInvite, MeetingGroupInvite,
                                            MeetingInvitationSerializer,
                                            MeetingInvitationUpdateSerializer, MeetingSerializer,
                                            MeetingUserInvite)
from lego.apps.permissions.views import AllowedPermissionsMixin


class MeetingViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Meeting.objects.prefetch_related('invitations', 'invitations__user')
    permission_classes = (MeetingPermissions,)
    serializer_class = MeetingSerializer

    @decorators.detail_route(methods=['POST'], serializer_class=MeetingUserInvite)
    def invite_user(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        meeting.invite_user(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @decorators.detail_route(methods=['POST'], serializer_class=MeetingBulkInvite)
    def bulk_invite(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = serializer.validated_data['users']
        groups = serializer.validated_data['groups']
        if not len(users) and not len(groups):
            raise ValidationError({'error': 'No users or groups given'})

        for user in users:
            meeting.invite_user(user)
        for group in groups:
            meeting.invite_group(group)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @decorators.detail_route(methods=['POST'], serializer_class=MeetingGroupInvite)
    def invite_group(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data['group']
        meeting.invite_group(group)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class MeetingInvitationViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = MeetingInvitation.objects.select_related('user')
    permission_classes = (MeetingInvitationPermissions,)
    lookup_field = 'user__id'

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return MeetingInvitationUpdateSerializer
        return MeetingInvitationSerializer

    def get_queryset(self):
        return MeetingInvitation.objects.filter(meeting=self.kwargs['meeting_pk'])


class MeetingInvitationTokenViewSet(viewsets.ViewSet):
    """
    Accept or reject invitation

    Reject or accept invitation to meeting. It is genereated when
    user is invited to a meeting, and sendt in the invitation email.

    To accept: [accept/?token=yourtoken](accept/)

    To reject: [reject/?token=yourtoken](reject/)
    """
    permission_classes = (MeetingIntitationTokenPermission, )

    @decorators.list_route(methods=['GET'])
    def accept(self, request):
        invitation = request.token_invitation
        invitation.accept()
        return Response(data=MeetingInvitationSerializer(invitation).data)

    def list(self, request):
        invitation = request.token_invitation
        return Response(data=MeetingInvitationSerializer(invitation).data)

    @decorators.list_route(methods=['GET'])
    def reject(self, request):
        invitation = request.token_invitation
        invitation.reject()
        return Response(data=MeetingInvitationSerializer(invitation).data)
