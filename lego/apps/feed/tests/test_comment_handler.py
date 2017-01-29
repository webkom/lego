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

    def test_comments_created_and_deleted(self):
        comment1 = self.comments[0]
        comment2 = self.comments[1]

        self.handler.handle_create(comment1)
        self.assertEqual(len(UserFeed(self.users[0].id)[0][0].activity_ids), 1)
        self.handler.handle_create(comment1)
        self.assertEqual(len(UserFeed(self.users[0].id)[0][0].activity_ids), 1)
        self.handler.handle_create(comment2)
        self.assertEqual(len(UserFeed(self.users[0].id)[0][0].activity_ids), 2)

        self.handler.handle_delete(comment1)
        self.assertEqual(len(UserFeed(self.users[0].id)[0][0].activity_ids), 1)
        self.handler.handle_delete(comment1)
        self.assertEqual(len(UserFeed(self.users[0].id)[0][0].activity_ids), 1)
        self.handler.handle_delete(comment2)
        # feed item is deleted
        self.assertEqual(len(UserFeed(self.users[0].id)[0]), 0)
