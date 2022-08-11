from unittest.mock import patch

from lego.apps.meetings.models import Meeting
from lego.apps.meetings.notifications import (
    MeetingInvitationNotification,
    MeetingInvitationReminderNotification,
)
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


@patch("lego.utils.email.django_send_mail")
class MeetingInvitationNotificationTestCase(BaseTestCase):
    fixtures = [
        "test_meetings.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        user = User.objects.all().first()
        meeting = Meeting.objects.all().first()
        meeting.created_by = user
        meeting.save()
        invitation, _created = meeting.invite_user(user)
        self.notifier = MeetingInvitationNotification(
            user, meeting_invitation=invitation
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["message"])
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_time(self, send_mail_mock):
        time = "01.10.16, kl. 19:15"
        self.assertEmailContains(send_mail_mock, time)

    def test_generate_email_content(self, send_mail_mock):
        content = "test user1 inviterte deg til et møte med tittel Bra møte."
        self.assertEmailContains(send_mail_mock, content)

    def test_generate_email_name(self, send_mail_mock):
        opening = "Hei, test!"
        self.assertEmailContains(send_mail_mock, opening)


@patch("lego.utils.email.django_send_mail")
class MeetingInvitationReminderTestCase(BaseTestCase):
    fixtures = [
        "test_meetings.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        user = User.objects.all().first()
        meeting = Meeting.objects.all().first()
        meeting.created_by = user
        meeting.save()
        invitation, _created = meeting.invite_user(user)
        self.notifier = MeetingInvitationReminderNotification(
            user, meeting_invitation=invitation
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["message"])
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_time(self, send_mail_mock):
        time = "01.10.16, kl. 19:15"
        self.assertEmailContains(send_mail_mock, time)

    def test_generate_email_content(self, send_mail_mock):
        content = (
            "Du har enda ikke svart på møteinnkalling til møtet med tittel Bra møte!"
        )
        self.assertEmailContains(send_mail_mock, content)

    def test_generate_email_name(self, send_mail_mock):
        opening = "Hei, test!"
        self.assertEmailContains(send_mail_mock, opening)
