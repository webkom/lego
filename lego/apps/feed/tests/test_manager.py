import os
from unittest import mock, skipIf

from stream_framework.feed_managers.base import add_operation, remove_operation

from lego.apps.comments.models import Comment
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.feed.verbs import CommentVerb


@skipIf(os.getenv('DRONE', False), 'Not running cassandra tests in drone')
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
        feed_manager.add_activity(self.activity, ['test1', 'test2'], [NotificationFeed])

        self.assertIn(self.activity, self.all_activities(NotificationFeed('test1')))
        self.assertIn(self.activity, self.all_activities(NotificationFeed('test2')))
        self.assertNotIn(self.activity, self.all_activities(NotificationFeed('useradmin_test')))

    def test_adding_actitivites_to_aggregated_feeds(self):
        feed_manager.add_activity(self.activity, ['test1', 'test2'], [UserFeed])
        feed_manager.add_activity(self.activity, ['useradmin_test', 'test2'], [PersonalFeed])

        self.assertIn(self.activity, self.all_activities(UserFeed('test1')))
        self.assertIn(self.activity, self.all_activities(UserFeed('test2')))
        self.assertNotIn(self.activity, self.all_activities(UserFeed('useradmin_test')))

        self.assertNotIn(self.activity, self.all_activities(PersonalFeed('test1')))
        self.assertIn(self.activity, self.all_activities(PersonalFeed('test2')))
        self.assertIn(self.activity, self.all_activities(PersonalFeed('useradmin_test')))

    @mock.patch('lego.apps.feed.feed_manager.feed_manager.create_fanout_tasks')
    def test_add_activity(self, mock_create_fanout_tasks):
        """Make sure the create_fanout_tasks function is called with the right arguments on add"""

        activity_mock = mock.Mock()

        feed_manager.add_activity(
            activity_mock,
            ['abc', 'def'],
            [NotificationFeed]
        )

        self.assertIn({'abc', 'def'}, mock_create_fanout_tasks.call_args[0])
        self.assertIn(NotificationFeed, mock_create_fanout_tasks.call_args[0])
        self.assertIn(add_operation, mock_create_fanout_tasks.call_args[0])

    @mock.patch('lego.apps.feed.feed_manager.feed_manager.create_fanout_tasks')
    def test_remove_activity(self, mock_create_fanout_tasks):
        """Make sure the create_fanout_tasks function is called with the right arguments on
        remove"""

        activity_mock = mock.Mock()

        feed_manager.remove_activity(
            activity_mock,
            ['abc', 'def'],
            [NotificationFeed]
        )

        self.assertIn({'abc', 'def'}, mock_create_fanout_tasks.call_args[0])
        self.assertIn(NotificationFeed, mock_create_fanout_tasks.call_args[0])
        self.assertIn(remove_operation, mock_create_fanout_tasks.call_args[0])
