from rest_framework.test import APITestCase

from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import AnnouncementVerb
from lego.apps.notifications.models import Announcement
from lego.apps.users.models import User


class FeedContextTestCase(APITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_authenticate(self.user)

    def _create_announcement_notification(self, message, from_group=None):
        announcement = Announcement.objects.create(
            message=message, from_group=from_group
        )
        activity = Activity(
            actor=self.user,
            verb=AnnouncementVerb,
            object=announcement,
            time=announcement.created_at,
        )
        feed_manager.add_activity(activity, [self.user.id], [NotificationFeed])
        return announcement

    def test_announcement_context(self):
        self._create_announcement_notification(message="Test announcement")

        response = self.client.get("/api/v1/feed-notifications/")
        self.assertEqual(response.status_code, 200)

        item = response.json()["results"][0]
        object_key = item["lastActivity"]["object"]

        self.assertIn(object_key, item["context"])
        announcement_context = item["context"][object_key]
        self.assertEqual(
            announcement_context["contentType"], "notifications.announcement"
        )
        self.assertEqual(announcement_context["message"], "Test announcement")
