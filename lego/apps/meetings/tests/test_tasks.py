from datetime import timedelta
from unittest import mock

from django.utils import timezone

from lego.apps.meetings import constants
from lego.apps.meetings.models import Meeting, MeetingInvitation
from lego.apps.meetings.notifications import MeetingInvitationReminderNotification
from lego.apps.meetings.tasks import notify_user_of_unanswered_meeting_invitation
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


@mock.patch("lego.apps.meetings.tasks.MeetingInvitationReminderNotification.notify")
class RegistrationReminderTestCase(BaseTestCase):
    fixtures = [
        "test_meetings.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        self.meeting = Meeting.objects.first()
        self.meeting.created_at = timezone.now() - timedelta(days=3)
        self.meeting.start_time = timezone.now() + timedelta(days=1)

        self.recipient = User.objects.first()

        self.meeting_invitation = MeetingInvitation.objects.get_or_create(
            meeting=self.meeting, user=self.recipient
        )[0]

        self.notifier = MeetingInvitationReminderNotification(
            self.recipient, meeting_invitation=self.meeting_invitation
        )

    def test_meeting_has_been_conducted(self, mock_notification):
        self.meeting.start_time = timezone.now()
        self.meeting.save()
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_not_called()

    def test_meeting_has_not_been_conducted(self, mock_notification):
        self.meeting.start_time = timezone.now() + timedelta(days=1)
        self.meeting.save()
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_called()

    def test_meeting_is_older_than_two_days(self, mock_notification):
        self.meeting.created_at = timezone.now() - timedelta(days=3)
        self.meeting.save()
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_called()

    def test_meeting_is_not_older_than_two_days(self, mock_notification):
        self.meeting.created_at = timezone.now() - timedelta(days=1)
        self.meeting.save()
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_not_called()

    def test_meeting_is_two_days_away(self, mock_notification):
        self.meeting.start_time = timezone.now() + timedelta(days=2)
        self.meeting.save()
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_not_called()

    def test_user_has_answered_invitation(self, mock_notification):
        self.meeting_invitation.status = constants.ATTENDING
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_not_called()

    def test_user_has_not_answered_invitation(self, mock_notification):
        self.meeting_invitation.status = constants.NO_ANSWER
        self.meeting.save()
        notify_user_of_unanswered_meeting_invitation.delay()
        mock_notification.assert_called()
