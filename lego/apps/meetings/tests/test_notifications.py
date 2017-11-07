from django.test import TestCase

from lego.apps.meetings.models import Meeting
from lego.apps.meetings.notifications import MeetingInvitationNotification
from lego.apps.users.models import User


class MeetingInvitationNotificationTestCase(TestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_meetings.yaml', 'test_users.yaml', 'initial_files.yaml']

    def test_generate_email_timezone(self):
        user = User.objects.all().first()
        meeting = Meeting.objects.all().first()
        meeting.created_by = user
        meeting.save()
        invitation, _created = meeting.invite_user(user)
        notifier = MeetingInvitationNotification(user, meeting=meeting, meeting_invitation=invitation)
        result = notifier.generate_mail()
        print(result)
