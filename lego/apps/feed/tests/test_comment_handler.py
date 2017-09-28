from django.contrib.contenttypes.models import ContentType

from lego.apps.comments.models import Comment
from lego.apps.events.models import Event
from lego.apps.feed.feed_handlers import CommentHandler
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.followers.models import FollowEvent
from lego.apps.users.models import User
from lego.utils.content_types import instance_to_string


class TestCommentHandler(FeedTestBase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml', 'test_comments.yaml',
        'test_companies.yaml', 'test_events.yaml', 'test_followevent.yaml'
    ]

    def setUp(self):
        self.comments = Comment.objects.all()
        self.handler = CommentHandler()
        self.users = User.objects.all()

        self.comment1 = self.comments[0]
        self.comment2 = self.comments[1]
        self.feed = UserFeed(self.comment1.created_by.pk)

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

    def test_comment_on_followed_event(self):
        follow = FollowEvent.objects.filter(pk=2).first()

        comment = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(Event),
            object_id=follow.target.id
        ).first()

        follower_feed = PersonalFeed(follow.follower.id)
        creator_feed = PersonalFeed(comment.created_by.id)

        self.assertIsNotNone(comment)

        self.assertEqual(self.activity_count(creator_feed), 0)
        self.assertEqual(self.activity_count(follower_feed), 0)
        self.handler.handle_create(comment)
        self.assertEqual(self.activity_count(creator_feed), 0)
        self.assertEqual(self.activity_count(follower_feed), 1)
        activity = self.all_activities(follower_feed)[0]
        self.assertEqual(activity.object, instance_to_string(comment))

        self.handler.handle_delete(comment)
        self.assertEqual(self.activity_count(follower_feed), 0)
        self.assertEqual(self.activity_count(creator_feed), 0)
