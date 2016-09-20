from django.test import TestCase

from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User


class MeetingTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def test_can_invite(self):
        user = User.objects.get(id=1)
        meeting = Meeting.objects.get(id=1)
        invitation = meeting.invite(user)[0]
        self.assertEqual(invitation.user, user)
        self.assertEqual(invitation.meeting, meeting)

    def test_can_accept_invite(self):
        """
        Check that a user may be invited, can accept the invitation,
        and is in the list of participants for the meeting.
        """
        user = User.objects.get(id=1)
        meeting = Meeting.objects.get(id=1)
        invitation = meeting.invite(user)[0]
        invitation.accept()
        self.assertIsNotNone(meeting.participants.get(user=user))
