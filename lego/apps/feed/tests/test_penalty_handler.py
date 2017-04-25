import os
from unittest import skipIf

from lego.apps.events.models import Event
from lego.apps.feed.feed_handlers import PenaltyHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.users.models import Penalty, User


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
            user=self.user,
            weight=1,
            reason='test',
            source_event=self.events.first()
        )
        feed_manager.remove_activity(
            self.all_activities(NotificationFeed(self.user.id))[0],
            [self.user.id],
            [NotificationFeed]
        )

    def test_create(self):
        self.assertEqual(self.activity_count(NotificationFeed(self.user.id)), 0)
        self.handler.handle_create(self.penalty)
        self.assertEqual(self.activity_count(NotificationFeed(self.user.id)), 1)

    def test_duplicate_create(self):
        self.handler.handle_create(self.penalty)
        self.assertEqual(self.activity_count(NotificationFeed(self.user.id)), 1)

        self.handler.handle_create(self.penalty)
        self.assertEqual(self.activity_count(NotificationFeed(self.user.id)), 1)

    def test_extra_content(self):
        self.handler.handle_create(self.penalty)

        activity = self.all_activities(NotificationFeed(self.user.id))[0]
        self.assertIn('reason', activity.extra_context)
        self.assertIn('weight', activity.extra_context)
        self.assertIn('total', activity.extra_context)
        self.assertEqual(activity.extra_context['reason'], self.penalty.reason)
        self.assertEqual(activity.extra_context['weight'], self.penalty.weight)
        self.assertEqual(activity.extra_context['total'], self.user.number_of_penalties())
