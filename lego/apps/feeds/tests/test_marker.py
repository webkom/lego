from rest_framework.test import APITestCase

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import AnnouncementVerb, MeetingInvitationVerb
from lego.apps.meetings.models import Meeting
from lego.apps.notifications.models import Announcement
from lego.apps.users.models import User


class FeedMarkerTestCase(APITestCase):
    fixtures = ["test_meetings.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_authenticate(self.user)
        NotificationFeed.mark_all(self.user.id, seen=True, read=True)

        announcement = Announcement.objects.create(message="Test announcement")
        feed_manager.add_activity(
            Activity(
                actor=self.user,
                verb=AnnouncementVerb,
                object=announcement,
                time=announcement.created_at,
            ),
            [self.user.id],
            [NotificationFeed],
        )

        invitation, _ = Meeting.objects.get(id=1).invite_user(self.user)
        feed_manager.add_activity(
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

    def test_mark(self):
        item1, item2 = NotificationFeed.objects.order_by("pk")

        response = self.client.post(
            f"/api/v1/feed-notifications/{item1.pk}/mark/", {"seen": True, "read": True}
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(item1.is_read)
        self.assertTrue(item1.is_seen)
        self.assertFalse(item2.is_read)
        self.assertFalse(item2.is_seen)
