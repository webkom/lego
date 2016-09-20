from django.test import TestCase

from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.users.models import User


class MeetingTestCase(TestCase):
    fixtures = ['development_meetings.yaml', 'test_users.yaml']

    def test_can_invite(self):
        user = User.objects.get(id=1)
        meeting = Meeting.objects.get(id=1)
        invitation = meeting.invite(user)
#         self.assertEqual(invitation.user, user)
#         self.assertEqual(invitation.meeting, meeting)



