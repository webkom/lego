import structlog
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.stats.utils import track

from .serializers import SlackInviteSerializer
from .utils import SlackException, SlackInvite

log = structlog.get_logger()


class SlackInviteViewSet(viewsets.ViewSet):
    """
    Invite an email to our slack team.
    """

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = SlackInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        email = serializer.validated_data['email']

        try:
            slack_invite = SlackInvite()
            slack_invite.invite(email)
            track(self.request.user, 'slack.invite', properties={'email': email})
        except SlackException as ex:
            log.warn('slack_invite_failed', email=email, exception=str(ex))
            raise exceptions.ValidationError({'detail': str(ex)})
