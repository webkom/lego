from unittest import mock

from django.test import TestCase
from stream_framework.feed_managers.base import add_operation, remove_operation

from lego.app.feed.feeds import NotificationFeed
from lego.app.feed.managers import notification_feed_manager
from lego.users.models import User


class NotificationFeedManagerTestCase(TestCase):

    fixtures = ['test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)

    def test_get_feed(self):
        """Check the get_user_feed function. The function should return a NotificationFeed based on
        the user id. Check the storage key."""

        feed = notification_feed_manager.get_user_feed(self.user.id)
        self.assertTrue(isinstance(feed, NotificationFeed))
        self.assertEqual(feed.feed_markers.base_key, 'feed:notification:1')

    @mock.patch('lego.app.feed.managers.notification_feed_manager.create_fanout_tasks')
    def test_add_activity(self, mock_create_fanout_tasks):
        """Make sure the create_fanout_tasks function is called with the right arguments on add"""

        activity_mock = mock.Mock()

        notification_feed_manager.add_activity(
            [1, 2],
            activity_mock
        )

        self.assertIn([1, 2], mock_create_fanout_tasks.call_args[0])
        self.assertIn(NotificationFeed, mock_create_fanout_tasks.call_args[0])
        self.assertIn(add_operation, mock_create_fanout_tasks.call_args[0])

    @mock.patch('lego.app.feed.managers.notification_feed_manager.create_fanout_tasks')
    def test_remove_activity(self, mock_create_fanout_tasks):
        """Make sure the create_fanout_tasks function is called with the right arguments on
        remove"""

        activity_mock = mock.Mock()

        notification_feed_manager.remove_activity(
            [1, 2],
            activity_mock
        )

        self.assertIn([1, 2], mock_create_fanout_tasks.call_args[0])
        self.assertIn(NotificationFeed, mock_create_fanout_tasks.call_args[0])
        self.assertIn(remove_operation, mock_create_fanout_tasks.call_args[0])
