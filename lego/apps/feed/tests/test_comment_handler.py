from lego.apps.comments.models import Comment
from lego.apps.feed.feed_handlers import CommentHandler
from lego.apps.feed.feeds.user.feed import UserFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.users.models import User


class TestCommentHandler(FeedTestBase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml', 'test_comments.yaml'
    ]

    def setUp(self):
        self.comments = Comment.objects.all()
        self.handler = CommentHandler()
        self.users = User.objects.all()

        self.comment1 = self.comments[0]
        self.comment2 = self.comments[1]
        self.feed = UserFeed(self.comment1.created_by.id)

    def test_duplicate_create(self):
        self.handler.handle_create(self.comment1)
        self.assertEqual(self.activity_count(self.feed), 1)

        self.handler.handle_create(self.comment1)
        self.assertEqual(self.activity_count(self.feed), 1)

    def test_comment_delete(self):
        self.handler.handle_create(self.comment1)
        self.handler.handle_create(self.comment2)
        self.assertEqual(self.activity_count(self.feed), 2)

        self.handler.handle_delete(self.comment1)
        self.assertEqual(self.activity_count(self.feed), 1)

        self.handler.handle_delete(self.comment1)
        self.assertEqual(self.activity_count(self.feed), 1)

        self.handler.handle_delete(self.comment2)
        self.assertEqual(len(self.feed[:]), 0)

    def test_extra_context(self):
        self.handler.handle_create(self.comment1)

        activity = self.all_activities(self.feed)[0]
        self.assertIn('content', activity.extra_context)
        self.assertEqual(activity.extra_context['content'], self.comment1.text)
