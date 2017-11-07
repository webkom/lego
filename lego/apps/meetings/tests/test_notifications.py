from unittest.mock import patch

from django.test import TestCase

from lego.apps.meetings.models import Meeting
from lego.apps.meetings.notifications import MeetingInvitationNotification
from lego.apps.users.models import User


@patch('lego.utils.email.django_send_mail')
class MeetingInvitationNotificationTestCase(TestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml',
                'test_users.yaml', 'initial_files.yaml']

    def setUp(self):
        user = User.objects.all().first()
        meeting = Meeting.objects.all().first()
        meeting.created_by = user
        meeting.save()
        invitation, _created = meeting.invite_user(user)
        self.notifier = MeetingInvitationNotification(
            user,
            meeting=meeting,
            meeting_invitation=invitation
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args['message'])
        self.assertIn(content, email_args['html_message'])

    def test_generate_email_time(self, send_mail_mock):
        time = '01.10.16, kl. 19:15'
        self.assertEmailContains(send_mail_mock, time)

    def test_generate_email_content(self, send_mail_mock):
        content = 'test user1 inviterte deg til et møte med tittel Bra møte.'
        self.assertEmailContains(send_mail_mock, content)

    def test_generate_email_name(self, send_mail_mock):
        opening = 'Hei test user1!'
        self.assertEmailContains(send_mail_mock, opening)
