from unittest import mock

from stream_framework.feed_managers.base import add_operation, remove_operation

from lego.apps.comments.models import Comment
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.feed.verbs import CommentVerb


class ManagerTestCase(FeedTestBase):

    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml', 'test_comments.yaml'
    ]

    def setUp(self):
        self.comment = Comment.objects.first()
        self.activity = Activity(
            actor=self.comment.created_by,
            verb=CommentVerb,
            object=self.comment,
            target=self.comment.content_object
        )

    def test_adding_actitivites_to_notification_feeds(self):
        feed_manager.add_activity(self.activity, [1, 2], [NotificationFeed])

        self.assertIn(self.activity, self.all_activities(NotificationFeed(1)))
        self.assertIn(self.activity, self.all_activities(NotificationFeed(2)))
        self.assertNotIn(self.activity, self.all_activities(NotificationFeed(3)))

    def test_adding_actitivites_to_aggregated_feeds(self):
        feed_manager.add_activity(self.activity, [1, 2], [UserFeed])
        feed_manager.add_activity(self.activity, [3, 2], [PersonalFeed])

        self.assertIn(self.activity, self.all_activities(UserFeed(1)))
        self.assertIn(self.activity, self.all_activities(UserFeed(2)))
        self.assertNotIn(self.activity, self.all_activities(UserFeed(3)))

        self.assertNotIn(self.activity, self.all_activities(PersonalFeed(1)))
        self.assertIn(self.activity, self.all_activities(PersonalFeed(2)))
        self.assertIn(self.activity, self.all_activities(PersonalFeed(3)))

    @mock.patch('lego.apps.feed.feed_manager.feed_manager.create_fanout_tasks')
    def test_add_activity(self, mock_create_fanout_tasks):
        """Make sure the create_fanout_tasks function is called with the right arguments on add"""

        activity_mock = mock.Mock()

        feed_manager.add_activity(
            activity_mock,
            [1, 2],
            [NotificationFeed]
        )

        self.assertIn({1, 2}, mock_create_fanout_tasks.call_args[0])
        self.assertIn(NotificationFeed, mock_create_fanout_tasks.call_args[0])
        self.assertIn(add_operation, mock_create_fanout_tasks.call_args[0])

    @mock.patch('lego.apps.feed.feed_manager.feed_manager.create_fanout_tasks')
    def test_remove_activity(self, mock_create_fanout_tasks):
        """Make sure the create_fanout_tasks function is called with the right arguments on
        remove"""

        activity_mock = mock.Mock()

        feed_manager.remove_activity(
            activity_mock,
            [1, 2],
            [NotificationFeed]
        )

        self.assertIn({1, 2}, mock_create_fanout_tasks.call_args[0])
        self.assertIn(NotificationFeed, mock_create_fanout_tasks.call_args[0])
        self.assertIn(remove_operation, mock_create_fanout_tasks.call_args[0])
