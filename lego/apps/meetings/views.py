from rest_framework import decorators, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from lego.apps.achievements.promotion import check_meeting_hidden
from lego.apps.meetings.authentication import MeetingInvitationTokenAuthentication
from lego.apps.meetings.filters import MeetingFilterSet
from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.meetings.serializers import (
    MeetingBulkInvite,
    MeetingDetailSerializer,
    MeetingGroupInvite,
    MeetingInvitationSerializer,
    MeetingInvitationUpdateSerializer,
    MeetingListSerializer,
    MeetingUserInvite,
)
from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.permissions.utils import get_permission_handler


class MeetingViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    filterset_class = MeetingFilterSet
    serializer_class = MeetingDetailSerializer

    def get_queryset(self):
        if self.request is None:
            return Meeting.objects.none()

        permission_handler = get_permission_handler(Meeting)
        return permission_handler.filter_queryset(
            self.request.user,
            Meeting.objects.prefetch_related("invitations", "invitations__user"),
        )

    def get_ordering(self):
        ordering = self.request.query_params.get("ordering", None)
        if ordering in ["start_time", "-start_time"]:
            return ordering
        return "start_time"

    def get_serializer_class(self):
        if self.action in ["list", "recurring"]:
            return MeetingListSerializer
        return super().get_serializer_class()

    @decorators.action(
        detail=True, methods=["POST"], serializer_class=MeetingUserInvite
    )
    def invite_user(self, request, *args, **kwargs):
        meeting: Meeting = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        meeting.invite_user(user, request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @decorators.action(
        detail=True, methods=["POST"], serializer_class=MeetingBulkInvite
    )
    def bulk_invite(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = serializer.validated_data["users"]
        groups = serializer.validated_data["groups"]
        if not len(users) and not len(groups):
            raise ValidationError({"error": "No users or groups given"})
        if len(users) == 1:
            check_meeting_hidden(
                owner=meeting.created_by, user=users[0], meeting=meeting
            )
        for user in users:
            meeting.invite_user(user, request.user)
        for group in groups:
            meeting.invite_group(group, request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @decorators.action(
        detail=True, methods=["POST"], serializer_class=MeetingGroupInvite
    )
    def invite_group(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data["group"]
        meeting.invite_group(group, request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @decorators.action(
        detail=False,
        methods=["GET"],
        url_path="templates",
        url_name="templates",
    )
    def templates(self, request, *args, **kwargs):
        meetings = self.get_queryset().filter(is_template=True, created_by=request.user)
        serializer = self.get_serializer(meetings, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class MeetingInvitationViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = MeetingInvitation.objects.select_related("user")
    lookup_field = "user__id"

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return MeetingInvitationUpdateSerializer
        return MeetingInvitationSerializer

    def get_queryset(self):
        if self.request is None:
            return MeetingInvitation.objects.none()

        return MeetingInvitation.objects.filter(meeting=self.kwargs["meeting_pk"])


class MeetingInvitationTokenViewSet(viewsets.ViewSet):
    """
    Accept or reject invitation

    Reject or accept invitation to meeting. It is genereated when
    user is invited to a meeting, and sendt in the invitation email.

    To accept: [accept/?token=yourtoken](accept/)

    To reject: [reject/?token=yourtoken](reject/)
    """

    authentication_classes = (MeetingInvitationTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    @decorators.action(detail=False, methods=["POST"])
    def accept(self, request):
        invitation = request.token_invitation
        invitation.accept()
        return Response(data=MeetingInvitationSerializer(invitation).data)

    def list(self, request):
        invitation = request.token_invitation
        return Response(data=MeetingInvitationSerializer(invitation).data)

    @decorators.action(detail=False, methods=["POST"])
    def reject(self, request):
        invitation = request.token_invitation
        invitation.reject()
        return Response(data=MeetingInvitationSerializer(invitation).data)
