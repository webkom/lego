import os
from unittest import skipIf

from lego.apps.events.models import Event
from lego.apps.feed.feed_handlers import PenaltyHandler
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.users.models import User, Penalty
from lego.utils.content_types import instance_to_string


@skipIf(os.getenv('DRONE', False), 'Not running cassandra tests in drone')
class TestPenaltyHandler(FeedTestBase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml'
                ]

    def setUp(self):
        self.events = Event.objects.all()
        self.handler = PenaltyHandler()
        self.user = User.objects.first()
        self.penalty = Penalty.objects.create(
            user = self.user,
            weight = 1,
            reason = 'test',
            source_event = self.events.first()
        )

    def test_duplicate_create(self):
        self.handler.handle_create(self.penalty)
        self.assertEqual(self.activity_count(NotificationFeed(self.user.id)), 1)

        self.handler.handle_create(self.penalty)
        self.assertEqual(self.activity_count(NotificationFeed(self.users.first().id)), 1)

    """def test_event_delete(self):
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
        self.assertEqual(self.activity_count(follower_feed), 0)"""