
from lego.apps.notifications.constants import MEETING_INVITE
from lego.apps.notifications.notification import Notification


class MeetingInvitationNotification(Notification):

    name = MEETING_INVITE

    def generate_mail(self):
        meeting_invitation = self.kwargs['meeting_invitation']
        meeting = meeting_invitation.meeting
        token = meeting_invitation.generate_invitation_token()

        return self._delay_mail(
            to_email=self.user.email_address,
            context={
                'name': self.user.full_name,
                'owner': meeting.created_by.full_name,
                'meeting_id': meeting.id,
                'meeting_title': meeting.title,
                "report_author":
                    meeting.report_author.full_name if meeting.report_author else 'Ikke valgt',
                'token': token
            },
            subject=f'Invitasjon til møte: {meeting.title}',
            plain_template='meetings/email/meeting_invitation.txt',
            html_template='meetings/email/meeting_invitation.html',
        )
