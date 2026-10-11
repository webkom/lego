from django.test import TransactionTestCase

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import AnnouncementVerb, MeetingInvitationVerb
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.users.models import User


class FeedManagerTestCase(TransactionTestCase):
    fixtures = ["test_abakus_groups.yaml", "test_meetings.yaml", "test_users.yaml"]

    def setUp(self):
        self.manager = feed_manager
        self.user = User.objects.get(id=1)

    def tearDown(self):
        NotificationFeed.mark_all(self.user.id, seen=True, read=True)

    def _add_announcement(self):
        announcement = Announcement.objects.create(message="Test announcement")
        self.manager.add_activity(
            Activity(
                actor=self.user,
                verb=AnnouncementVerb,
                object=announcement,
                time=announcement.created_at,
            ),
            [self.user.id],
            [NotificationFeed],
        )

    def _add_meeting_invitation(self, meeting_id=1):
        invitation, _ = Meeting.objects.get(id=meeting_id).invite_user(self.user)
        self.manager.add_activity(
            Activity(
                actor=self.user,
                verb=MeetingInvitationVerb,
                object=invitation,
                target=invitation.user,
                time=invitation.created_at,
            ),
            [self.user.id],
            [NotificationFeed],
        )

    def test_meeting_invitation_activity(self):
        meeting = Meeting.objects.get(id=1)
        meeting2 = Meeting.objects.get(id=2)
        meeting_invitation, _ = meeting.invite_user(self.user)
        meeting_invitation2, _ = meeting2.invite_user(self.user)

        # Add first activity
        activity = Activity(
            actor=self.user,
            verb=MeetingInvitationVerb,
            object=meeting_invitation,
            target=meeting_invitation.user,
            time=meeting_invitation.created_at,
        )
        self.manager.add_activity(activity, [self.user.id], [NotificationFeed])
        self.assertEqual(1, NotificationFeed.objects.count())

        # Add second activity in the same group
        activity1 = Activity(
            actor=self.user,
            verb=MeetingInvitationVerb,
            object=meeting_invitation2,
            target=meeting_invitation.user,
            time=meeting_invitation.created_at,
        )
        self.manager.add_activity(activity1, [self.user.id], [NotificationFeed])
        self.assertEqual(1, NotificationFeed.objects.count())

        # Remove fist activity
        self.manager.remove_activity(activity, [], [NotificationFeed])
        self.assertEqual(1, NotificationFeed.objects.count())

        # Remove the second activity and mage sure the aggregated activity is removed
        self.manager.remove_activity(activity1, [], [NotificationFeed])
        self.assertEqual(0, NotificationFeed.objects.count())

    def test_mark_activities(self):
        self._add_announcement()
        self._add_meeting_invitation()

        item1, item2 = NotificationFeed.objects.order_by("pk")
        self.assertFalse(item1.is_read)
        self.assertFalse(item1.is_seen)
        self.assertFalse(item2.is_read)
        self.assertFalse(item2.is_seen)
        self.assertEqual(
            {"unseen_count": 2, "unread_count": 2},
            NotificationFeed.get_notification_data(self.user.id),
        )

        ids1 = [a.activity_id for a in item1.activities]
        NotificationFeed.mark_activities(self.user.id, ids1, seen=True, read=True)

        self.assertTrue(item1.is_read)
        self.assertTrue(item1.is_seen)
        self.assertFalse(item2.is_read)
        self.assertFalse(item2.is_seen)
        self.assertEqual(
            {"unseen_count": 1, "unread_count": 1},
            NotificationFeed.get_notification_data(self.user.id),
        )
