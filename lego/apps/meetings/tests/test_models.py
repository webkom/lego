from django.test import TestCase

from lego.apps.meetings.models import Meeting
from lego.apps.users.models import User


class MeetingTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.meeting = Meeting.objects.get(id=1)

    def test_can_invite(self):
        invitation = self.meeting.invite(self.user)[0]
        self.assertEqual(invitation.user, self.user)
        self.assertEqual(invitation.meeting, self.meeting)

    def test_can_accept_invite(self):
        """
        Check that a user may be invited, can accept the invitation,
        and is in the list of participants.all() for the meeting.
        """
        invitation = self.meeting.invite(self.user)[0]
        invitation.accept()
        self.assertIn(self.user, self.meeting.participants.all())

    def test_double_invite(self):
        self.assertEqual(len(self.meeting.invited_users.all()), 0)
        self.assertEqual(len(self.meeting.participants.all()), 0)
        self.assertEqual(len(self.meeting.invitation.all()), 0)
        self.meeting.invite(self.user)[0].accept()
        self.meeting.invite(self.user)[0].accept()
        self.assertEqual(len(self.meeting.invited_users.all()), 1)
        self.assertEqual(len(self.meeting.participants.all()), 1)
        self.assertEqual(len(self.meeting.invitation.all()), 1)

    def test_participants(self):
        self.assertEqual(len(self.meeting.participants.all()), 0)
        self.meeting.invite(self.user)
        self.assertEqual(len(self.meeting.participants.all()), 0)
        invitation = self.meeting.invitation.get(user=self.user)
        invitation.accept()
        self.assertEqual(len(self.meeting.participants.all()), 1)
        invitation.reject()
        self.assertEqual(len(self.meeting.participants.all()), 0)

    def test_invited_users(self):
        self.assertEqual(len(self.meeting.invited_users.all()), 0)
        self.meeting.invite(self.user)
        self.assertEqual(len(self.meeting.invited_users.all()), 1)
        invitation = self.meeting.invitation.get(user=self.user)
        invitation.accept()
        self.assertEqual(len(self.meeting.invited_users.all()), 1)
        invitation.reject()
        self.assertEqual(len(self.meeting.invited_users.all()), 1)
        self.meeting.uninvite(self.user)
        self.assertEqual(len(self.meeting.invited_users.all()), 0)

    def test_delete_invitation_after_accept(self):
        self.meeting.invite(self.user)
        invitation = self.meeting.invitation.get(user=self.user)
        invitation.accept()
        self.meeting.uninvite(self.user)
        self.assertEqual(len(self.meeting.invited_users.all()), 0)
        self.assertEqual(len(self.meeting.participants.all()), 0)
        self.assertEqual(len(self.meeting.invitation.all()), 0)

