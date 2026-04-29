from zoneinfo import ZoneInfo

from django.utils import timezone

from lego.apps.meetings.models import MeetingInvitation
from lego.apps.notifications.constants import (
    MEETING_INVITATION_REMINDER,
    MEETING_INVITE,
)
from lego.apps.notifications.notification import Notification


class MeetingInvitationNotification(Notification):
    name = MEETING_INVITE

    def generate_mail(self):
        meeting_invitation = self.kwargs["meeting_invitation"]
        meeting = meeting_invitation.meeting
        token = meeting_invitation.generate_invitation_token()
        time = timezone.localtime(
            value=meeting.start_time, timezone=ZoneInfo("Europe/Oslo")
        )
        author = (
            meeting.report_author.full_name if meeting.report_author else "Ikke valgt"
        )

        start_time = time.strftime("%d.%m.%y, kl. %H:%M")

        return self._delay_mail(
            to_email=self.user.email_address,
            context={
                "first_name": self.user.first_name,
                "owner": meeting.created_by.full_name,
                "meeting_id": meeting.id,
                "meeting_title": meeting.title,
                "meeting_start_time": start_time,
                "report_author": author,
                "token": token,
            },
            subject=f"Invitasjon til møte: {meeting.title} - {start_time}",
            plain_template="meetings/email/meeting_invitation.txt",
            html_template="meetings/email/meeting_invitation.html",
        )

    def generate_push(self):
        meeting_invitation = self.kwargs["meeting_invitation"]
        meeting = meeting_invitation.meeting

        return self._delay_push(
            template="meetings/push/meeting_invitation.txt",
            context={
                "owner": meeting.created_by.full_name,
                "meeting_id": meeting.id,
                "meeting_title": meeting.title,
            },
            title="Invitasjon til møte",
            instance=meeting,
        )


class MeetingInvitationReminderNotification(Notification):
    name = MEETING_INVITATION_REMINDER

    def generate_mail(self):
        meeting_invitation: MeetingInvitation = self.kwargs["meeting_invitation"]

        meeting = meeting_invitation.meeting

        token = meeting_invitation.generate_invitation_token()

        time = timezone.localtime(
            value=meeting.start_time, timezone=ZoneInfo("Europe/Oslo")
        )
        start_time = time.strftime("%d.%m.%y, kl. %H:%M")

        author = (
            meeting.report_author.full_name if meeting.report_author else "Ikke valgt"
        )

        return self._delay_mail(
            to_email=self.user.email_address,
            context={
                "first_name": self.user.first_name,
                "meeting_id": meeting.id,
                "meeting_title": meeting.title,
                "meeting_start_time": start_time,
                "report_author": author,
                "token": token,
            },
            subject="Ikke svart på møteinnkalling",
            plain_template="meetings/email/meeting_invitation_reminder.txt",
            html_template="meetings/email/meeting_invitation_reminder.html",
        )

    def generate_push(self):
        meeting_invitation = self.kwargs["meeting_invitation"]
        meeting = meeting_invitation.meeting

        time = timezone.localtime(
            value=meeting.start_time, timezone=ZoneInfo("Europe/Oslo")
        )
        start_time = time.strftime("%d.%m.%y, kl. %H:%M")

        return self._delay_push(
            template="meetings/push/meeting_invitation_reminder.txt",
            context={
                "meeting_title": meeting.title,
                "meeting_start_time": start_time,
            },
            title="Ikke svart på møteinnkalling",
            instance=meeting,
        )
