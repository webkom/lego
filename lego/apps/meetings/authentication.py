from rest_framework import authentication

from lego.apps.meetings.models import MeetingInvitation


class MeetingInvitationTokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        raw_token = request.GET.get('token')
        if not raw_token:
            return

        invitation = MeetingInvitation.validate_token(raw_token)
        if not invitation:
            return

        request.token_invitation = invitation
        return invitation.user, raw_token
