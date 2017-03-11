import os
from datetime import timedelta
from unittest import skipIf

from django.utils import timezone

from lego.apps.events.models import Event, Registration
from lego.apps.feed.feed_handlers.registration_handler import RegistrationHandler
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.tests.feed_test_base import FeedTestBase
from lego.apps.users.models import AbakusGroup, User


@skipIf(os.getenv('DRONE', False), 'Not running cassandra tests in drone')
class TestRegistrationHandler(FeedTestBase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml'
                ]

    def setUp(self):
        self.event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.event.start_time = timezone.now() + timedelta(days=1)
        self.event.merge_time = timezone.now() + timedelta(hours=12)
        self.event.save()

        self.user = User.objects.first()

        self.handler = RegistrationHandler()
        self.feed = NotificationFeed(self.user.id)

    def test_bump(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.user)
        reg = Registration.objects.get_or_create(event=self.event, user=self.user)[0]
        self.event.register(reg)
        self.handler.handle_bump(reg)

        self.assertEqual(self.activity_count(self.feed), 1)
        act = self.all_activities(self.feed)[0]
        self.assertEqual(act.verb.infinitive, 'registration_bump')

    def test_admin_reg(self):
        self.event.admin_register(
            user=self.user,
            pool=self.event.pools.first(),
            admin_reason='test'
        )

        self.assertEqual(self.activity_count(self.feed), 1)
        act = self.all_activities(self.feed)[0]
        self.assertEqual(act.verb.infinitive, 'admin_registration')
