from lego.apps.meetings.models import Meeting, ReportChangelog
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class MeetingTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml", "test_meetings.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.meeting = Meeting.objects.get(id=3)

    def test_report_changelog_creation_on_report_update(self):
        # Create a changelog
        self.assertEqual(self.meeting.report_changelogs.count(), 0)
        new_report_content = "Et nytt og kulere referat!"
        self.meeting.report = new_report_content
        self.meeting.updated_by = self.user
        self.meeting.save()
        self.assertEqual(self.meeting.report_changelogs.count(), 1)

        # Check changelog properties
        changelog: ReportChangelog = self.meeting.report_changelogs.first()
        self.assertIsNotNone(changelog)
        self.assertEqual(changelog.report, new_report_content)
        self.assertEqual(changelog.created_by, self.user)

    def test_no_changelog_creation_on_same_report(self):
        self.assertEqual(self.meeting.report_changelogs.count(), 0)
        initial_report_content = "I dag skal vi diskutere om Webkom skal få bånd"
        self.meeting.report = initial_report_content
        self.meeting.save()
        self.assertEqual(self.meeting.report_changelogs.count(), 1)
        self.meeting.save()  # Save again
        self.assertEqual(self.meeting.report_changelogs.count(), 1)

    def test_can_invite(self):
        invitation = self.meeting.invite_user(self.user)[0]
        self.assertEqual(invitation.user, self.user)
        self.assertEqual(invitation.meeting, self.meeting)

    def test_can_accept_invite(self):
        invitation = self.meeting.invite_user(self.user)[0]
        invitation.accept()
        self.assertIn(self.user, self.meeting.participants.all())

    def test_double_invite(self):
        self.assertEqual(self.meeting.invited_users.count(), 0)
        self.assertEqual(self.meeting.participants.count(), 0)
        self.assertEqual(self.meeting.invitations.count(), 0)
        self.meeting.invite_user(self.user)[0].accept()
        self.meeting.invite_user(self.user)[0].accept()
        self.assertEqual(self.meeting.invited_users.count(), 1)
        self.assertEqual(self.meeting.participants.count(), 1)
        self.assertEqual(self.meeting.invitations.count(), 1)

    def test_participants(self):
        self.assertEqual(self.meeting.participants.count(), 0)
        self.meeting.invite_user(self.user)
        self.assertEqual(self.meeting.participants.count(), 0)
        invitation = self.meeting.invitations.get(user=self.user)
        invitation.accept()
        self.assertEqual(self.meeting.participants.count(), 1)
        invitation.reject()
        self.assertEqual(self.meeting.participants.count(), 0)

    def test_invited_users(self):
        self.assertEqual(self.meeting.invited_users.count(), 0)
        self.meeting.invite_user(self.user)
        self.assertEqual(self.meeting.invited_users.count(), 1)
        invitation = self.meeting.invitations.get(user=self.user)
        invitation.accept()
        self.assertEqual(self.meeting.invited_users.count(), 1)
        invitation.reject()
        self.assertEqual(self.meeting.invited_users.count(), 1)
        self.meeting.uninvite_user(self.user)
        self.assertEqual(self.meeting.invited_users.count(), 0)

    def test_delete_invitation_after_accept(self):
        self.meeting.invite_user(self.user)
        invitation = self.meeting.invitations.get(user=self.user)
        invitation.accept()
        self.meeting.uninvite_user(self.user)
        self.assertEqual(self.meeting.invited_users.count(), 0)
        self.assertEqual(self.meeting.participants.count(), 0)
        self.assertEqual(self.meeting.invitations.count(), 0)
