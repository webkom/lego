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
        self.assertIn(user, meeting.participants())

    def test_double_invite(self):
        user = User.objects.get(id=1)
        meeting = Meeting.objects.get(id=1)
        self.assertEqual(len(meeting.invited_users.all()), 0)
        self.assertEqual(len(meeting.participants()), 0)
        self.assertEqual(len(meeting.invitation.all()), 0)
        meeting.invite(user)[0].accept()
        meeting.invite(user)[0].accept()
        self.assertEqual(len(meeting.invited_users.all()), 1)
        self.assertEqual(len(meeting.participants()), 1)
        self.assertEqual(len(meeting.invitation.all()), 1)

    def test_participants(self):
        user = User.objects.get(id=1)
        meeting = Meeting.objects.get(id=1)
        self.assertEqual(len(meeting.participants()), 0)
        meeting.invite(user)
        self.assertEqual(len(meeting.participants()), 0)
        invitation = meeting.invitation.get(user=user)
        invitation.accept()
        self.assertEqual(len(meeting.participants()), 1)
        invitation.reject()
        self.assertEqual(len(meeting.participants()), 0)

    def test_invited_users(self):
        user = User.objects.get(id=1)
        meeting = Meeting.objects.get(id=1)
        self.assertEqual(len(meeting.invited_users.all()), 0)
        meeting.invite(user)
        self.assertEqual(len(meeting.invited_users.all()), 1)
        invitation = meeting.invitation.get(user=user)
        invitation.accept()
        self.assertEqual(len(meeting.invited_users.all()), 1)
        invitation.reject()
        self.assertEqual(len(meeting.invited_users.all()), 1)
        meeting.uninvite(user)
        self.assertEqual(len(meeting.invited_users.all()), 0)
