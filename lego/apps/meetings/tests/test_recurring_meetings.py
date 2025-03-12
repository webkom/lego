from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from lego.apps.meetings.models import Meeting
from lego.apps.meetings.tasks import generate_weekly_recurring_meetings
from lego.utils.test_utils import BaseTestCase


class GenerateRecurringMeetingsTestCase(BaseTestCase):

    def setUp(self):
        """Create all necessary test data instead of relying on fixtures."""

        User = get_user_model()

        # Create test users
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com"
        )

        # Define meeting attributes first
        title = "Weekly Standup"
        location = "Meeting Room A"
        description = "Recurring team standup"
        report = "Meeting report notes"

        # Create an initial recurring meeting template
        self.meeting = Meeting.objects.create(
            title=title,
            location=location,
            start_time=timezone.now() - timedelta(days=7),
            end_time=timezone.now() - timedelta(days=6, hours=23),
            description=description,
            is_recurring=True,  # Mark this as a recurring template
            is_template=True,  # This is a template meeting
            report=report,
            current_user=self.user1,
        )

        # Invite users to the meeting
        self.meeting.invite_user(self.user1)
        self.meeting.invite_user(self.user2)

    def test_creates_new_recurring_meeting(self):
        """Test that a new recurring meeting is created correctly."""
        generate_weekly_recurring_meetings()
        new_meeting = Meeting.objects.filter(parent=self.meeting).first()
        expected_week_number = timezone.localtime(new_meeting.start_time).isocalendar()[
            1
        ]
        expected_title = f"{self.meeting.title} [Uke {expected_week_number}]"
        self.assertIsNotNone(new_meeting, "No recurring meeting was created")
        self.assertEqual(new_meeting.title, expected_title, "Title should be the same")
        self.assertEqual(
            new_meeting.location, self.meeting.location, "Location should be the same"
        )
        self.assertFalse(
            new_meeting.is_template, "New meetings should not be templates"
        )
        self.assertEqual(
            new_meeting.invited_users.count(), 2, "Invited users should be copied over"
        )

    def test_does_not_duplicate_meetings_on_consecutive_runs(self):
        """Ensure running the task twice does not create duplicate meetings."""
        generate_weekly_recurring_meetings()
        generate_weekly_recurring_meetings()  # Run again immediately

        new_meetings = Meeting.objects.filter(parent=self.meeting)
        self.assertEqual(new_meetings.count(), 1, "Duplicate meetings were created")

    def test_invited_users_are_copied_to_new_meeting(self):
        """Ensure invited users are copied correctly to new meetings."""
        generate_weekly_recurring_meetings()

        new_meeting = Meeting.objects.filter(parent=self.meeting).first()
        invited_users = new_meeting.invited_users.all()

        self.assertIn(self.user1, invited_users, "User1 should be invited")
        self.assertIn(self.user2, invited_users, "User2 should be invited")
        self.assertEqual(invited_users.count(), 2, "All invited users should be copied")

    def test_does_not_create_meeting_if_future_meeting_exists(self):
        """Ensure a new meeting is not created if a future recurring meeting already exists."""
        generate_weekly_recurring_meetings()

        # Manually create a future meeting to simulate it already existing
        Meeting.objects.create(
            title=self.meeting.title,
            location=self.meeting.location,
            start_time=(timezone.now() + timedelta(days=7)),
            end_time=(timezone.now() + timedelta(days=7, hours=1)),
            description=self.meeting.description,
            is_recurring=False,
            parent=self.meeting,
            current_user=self.meeting.created_by,
        )

        generate_weekly_recurring_meetings()  # Should not create another one

        transaction.on_commit(
            lambda: self.assertEqual(
                Meeting.objects.filter(parent=self.meeting).count(),
                1,
                "A duplicate meeting was created even though one exists",
            )
        )
