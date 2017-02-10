from lego.apps.events.models import Event
from lego.apps.feed.feed_handlers import EventHandler
from lego.apps.feed.feeds.company_feed import CompanyFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.followers.models import FollowCompany
from lego.apps.users.models import User
from lego.utils.content_types import instance_to_string


class TestEventHandler(FeedTestBase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml', 'test_events.yaml',
        'test_followcompany.yaml'
    ]

    def setUp(self):
        self.events = Event.objects.all()
        self.handler = EventHandler()
        self.users = User.objects.all()

    def test_duplicate_create(self):
        self.handler.handle_create(self.events[0])
        self.assertEqual(self.activity_count(CompanyFeed(self.events[0].company_id)), 1)

        self.handler.handle_create(self.events[0])
        self.assertEqual(self.activity_count(CompanyFeed(self.events[0].company_id)), 1)

    def test_comment_delete(self):
        self.handler.handle_create(self.events[0])
        self.assertEqual(self.activity_count(CompanyFeed(self.events[0].company_id)), 1)
        self.handler.handle_create(self.events[1])
        self.assertEqual(self.activity_count(CompanyFeed(self.events[1].company_id)), 1)

        self.handler.handle_delete(self.events[0])
        self.assertEqual(self.activity_count(CompanyFeed(self.events[0].company_id)), 0)
        self.assertEqual(self.activity_count(CompanyFeed(self.events[1].company_id)), 1)

        self.handler.handle_delete(self.events[0])
        self.assertEqual(self.activity_count(CompanyFeed(self.events[0].company_id)), 0)

    def test_extra_context(self):
        self.handler.handle_create(self.events[0])

        activity = self.all_activities(CompanyFeed(self.events[0].company_id))[0]
        self.assertIn('title', activity.extra_context)
        self.assertEqual(activity.extra_context['title'], self.events[0].title)

    def test_create_with_personal_feed(self):
        follow = FollowCompany.objects.filter(pk=1).first()

        follower_feed = PersonalFeed(follow.follower.username)
        event = Event.objects.filter(company=follow.target).first()

        self.assertIsNotNone(event)

        self.assertEqual(self.activity_count(follower_feed), 0)
        self.handler.handle_create(event)
        self.assertEqual(self.activity_count(follower_feed), 1)
        activity = self.all_activities(follower_feed)[0]
        self.assertEqual(activity.object, instance_to_string(event))

        self.handler.handle_delete(event)
        self.assertEqual(self.activity_count(follower_feed), 0)
