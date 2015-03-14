from datetime import timedelta

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
        capacities_to_add = [10]
        for capacity in capacities_to_add:
            event.add_pool("1-5 klasse", capacity, timezone.now() - timedelta(hours=24))
        self.assertEqual(sum(capacities_to_add), event.capacity)

    def test_capacity_with_multiple_pools(self):
        event = Event.objects.get(title="NO_POOLS")
        capacities_to_add = [10, 20]
        for capacity in capacities_to_add:
            event.add_pool("pool", capacity, timezone.now() - timedelta(hours=24))
        self.assertEqual(sum(capacities_to_add), event.capacity)


class RegistrationTestCase(TestCase):
    fixtures = ['test_users.yaml', 'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(merge_time=timezone.now() + timedelta(hours=12))

    def get_dummy_users(self, n):
        users = []
        for i in range(n):
            first_name = last_name = username = email = str(i)
            user = User(username=username, first_name=first_name, last_name=last_name, email=email)
            user.save()
            users.append(user)
        return users

    def test_can_register_single_pool(self):
        user = self.get_dummy_users(1)[0]
        event = Event.objects.get(title="POOLS")
        pool = event.pools.first()
        event.register(user=user, pool=pool)
        self.assertEqual(pool.number_of_registrations, event.number_of_registrations)

    def test_waiting_list_if_full(self):
        event = Event.objects.get(title="POOLS")
        pool = event.pools.first()
        people_to_place_in_waiting_list = 3

        users = self.get_dummy_users(pool.capacity + 3)
        for user in users:
            event.register(user=user, pool=pool)

        self.assertEqual(event.waiting_list.number_of_registrations, people_to_place_in_waiting_list)
        self.assertEqual(event.number_of_registrations, pool.number_of_registrations)

    def test_number_of_waiting_registrations(self):
        event = Event.objects.get(title="POOLS")
        pool = event.pools.first()
        people_to_place_in_waiting_list = 3

        users = self.get_dummy_users(pool.capacity + 3)
        for user in users:
            event.register(user=user, pool=pool)

        self.assertEqual(event.number_of_waiting_registrations, people_to_place_in_waiting_list)

    def test_can_register_pre_merge(self):
        event = Event.objects.get(title="POOLS")
        pool_one = event.pools.first()
        pool_two = event.pools.get(pk=2)
        users = self.get_dummy_users(2)
        user_one, user_two = users[0], users[1]

        event.register(user=user_one, pool=pool_one)
        n_registrants = pool_one.number_of_registrations
        self.assertEqual(pool_one.number_of_registrations, event.number_of_registrations)

        event.register(user=user_two, pool=pool_two)
        n_registrants += pool_two.number_of_registrations
        self.assertEqual(n_registrants, event.number_of_registrations)

    def test_can_register_post_merge(self):
        event = Event.objects.get(title="NO_POOLS")
        event.merge_time = timezone.now() - timedelta(hours=12)
        pool_one = event.add_pool("1-2 klasse", 1, timezone.now() - timedelta(hours=24))
        pool_two = event.add_pool("3-5 klasse", 2, timezone.now() - timedelta(hours=24))
        users = self.get_dummy_users(3)
        pool_one_users = 2

        for user in users[:pool_one_users]:
            event.register(user=user, pool=pool_one)
        for user in users[pool_one_users:]:
            event.register(user=user, pool=pool_two)

        registrations = pool_one.number_of_registrations + pool_two.number_of_registrations
        self.assertEqual(registrations, event.number_of_registrations)

    def test_placed_in_waiting_list_post_merge(self):
        event = Event.objects.get(title="NO_POOLS")
        pool = event.add_pool("3-5 klasse", 2, timezone.now() - timedelta(hours=24))
        event.merge_time = timezone.now() - timedelta(hours=12)
        users = self.get_dummy_users(3)
        expected_users_in_waiting_list = 1

        for user in users:
            event.register(user, pool=pool)

        self.assertEqual(event.waiting_list.number_of_registrations, expected_users_in_waiting_list)

    def test_bump(self):
        event = Event.objects.get(title="POOLS")
        pool = event.pools.first()
        users = self.get_dummy_users(pool.capacity + 1)
        for user in users:
            event.register(user=user, pool=pool)

        waiting_list_before = event.number_of_waiting_registrations
        regs_before = event.number_of_registrations

        event.bump(pool=pool)

        self.assertEqual(event.number_of_registrations, regs_before+1)
        self.assertEqual(event.number_of_waiting_registrations, waiting_list_before-1)
