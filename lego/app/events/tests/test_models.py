from datetime import timedelta
import unittest

from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from lego.app.content.tests import ContentTestMixin
from lego.users.models import User
from lego.app.events.models import Event
from lego.app.events.views.events import EventViewSet


class EventTest(TestCase, ContentTestMixin):

    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_events.yaml']

    model = Event
    ViewSet = EventViewSet


class EventMethodTest(TestCase):
    fixtures = ['test_users.yaml', 'test_events.yaml']

    def setUp(self):
        self.event = Event.objects.get(pk=1)

    def test_str(self):
        self.assertEqual(str(self.event), self.event.title)

    def test_slug(self):
        self.assertEqual(slugify(self.event.title), self.event.slug())


class PoolCapacityTestCase(TestCase):
    fixtures = ['test_users.yaml', 'test_events.yaml']

    def test_capacity_with_single_pool(self):
        event = Event.objects.get(title="NO_POOLS")
        sizes_to_add = [10]
        for size in sizes_to_add:
            event.add_pool("1-5 klasse", size, timezone.now() - timedelta(hours=24))
        self.assertEqual(sum(sizes_to_add), event.total_capacity_count)

    def test_capacity_with_multiple_pools(self):
        event = Event.objects.get(title="NO_POOLS")
        sizes_to_add = [10, 20]
        for size in sizes_to_add:
            event.add_pool("pool", size, timezone.now() - timedelta(hours=24))
        self.assertEqual(sum(sizes_to_add), event.total_capacity_count)


class RegistrationTestCase(TestCase):
    fixtures = ['test_users.yaml', 'test_events.yaml']

    def setUp(self):
        event = Event.objects.get(pk=1)
        event.merge_time = timezone.now() + timedelta(hours=24)
        event.save()

    @unittest.expectedFailure
    def test_can_register_single_pool(self):
        event = Event.objects.get(pk=1)
        pool = event.add_pool("1-5 klasse", 1, timezone.now() - timedelta(hours=24))
        event.register(user=None, pool=pool)
        self.assertEqual(pool.number_of_registrations, event.total_registrations_count)

    @unittest.expectedFailure
    def test_unable_to_register_if_full(self):
        event = Event.objects.get(pk=1)
        pool = event.add_pool("1-5 klasse", 1, timezone.now() - timedelta(hours=24))
        event.register(user=None, pool=pool)
        self.assertRaises(EventFullException, event.register, None, pool)
        registrations = pool.number_of_registrations
        self.assertEqual(registrations, event.total_registrations_count)

    @unittest.expectedFailure
    def test_can_register_pre_merge(self):
        event = Event.objects.get(pk=1)
        pool_one = event.add_pool("1-2 klasse", 1, timezone.now() - timedelta(hours=24))
        pool_two = event.add_pool("3-5 klasse", 1, timezone.now() - timedelta(hours=24))
        event.register(user=None, pool=pool_one)
        capacity = pool_one.number_of_registrations
        self.assertEqual(pool_one.size, event.total_registrations_count)
        event.register(user=None, pool=pool_two)
        capacity += pool_two.number_of_registrations
        self.assertEqual(capacity, event.total_registrations_count)

    @unittest.expectedFailure
    def test_can_register_post_merge(self):
        event = Event.objects.get(pk=1)
        event.merge_time = timezone.now() - timedelta(hours=12)
        pool_one = event.add_pool("1-2 klasse", 1, timezone.now() - timedelta(hours=24))
        pool_two = event.add_pool("3-5 klasse", 2, timezone.now() - timedelta(hours=24))
        event.register(user=None, pool=pool_one)
        event.register(user=None, pool=pool_one)
        event.register(user=None, pool=pool_two)
        registrations = pool_one.number_of_registrations + pool_two.number_of_registrations
        self.assertEqual(registrations, event.total_registrations_count)

    @unittest.expectedFailure
    def test_unable_to_register_post_merge(self):
        event = Event.objects.get(pk=1)
        event.merge_time = timezone.now() - timedelta(hours=12)
        pool_one = event.add_pool("1-2 klasse", 1, timezone.now() - timedelta(hours=24))
        pool_two = event.add_pool("3-5 klasse", 2, timezone.now() - timedelta(hours=24))
        event.register(user=None, pool=pool_one)
        event.register(user=None, pool=pool_one)
        event.register(user=None, pool=pool_one)
        self.assertRaises(EventFullException, event.register, None, pool_two)
