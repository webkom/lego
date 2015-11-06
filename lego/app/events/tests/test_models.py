from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from lego.app.content.tests import ContentTestMixin
from lego.app.events.models import Event, Pool, Registration
from lego.app.events.views.events import EventViewSet
from lego.users.models import AbakusGroup, User


def get_dummy_users(n):
    users = []

    for i in range(n):
        first_name = last_name = username = email = str(i)
        user = User(username=username, first_name=first_name, last_name=last_name, email=email)
        user.save()
        users.append(user)

    return users


class EventTest(TestCase, ContentTestMixin):
    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_events.yaml']

    model = Event
    ViewSet = EventViewSet


class EventMethodTest(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        self.event = Event.objects.get(pk=1)

    def test_str(self):
        self.assertEqual(str(self.event), self.event.title)


class PoolMethodTest(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        self.pool = event.pools.first()

    def test_str(self):
        self.assertEqual(str(self.pool), self.pool.name)


class RegistrationMethodTest(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        self.registration = event.register(user=user, pool=pool)

    def test_str(self):
        d = {
            'user': self.registration.user,
            'pool': self.registration.pool,
        }

        self.assertEqual(str(self.registration), str(d))


class PoolCapacityTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def test_capacity_with_single_pool(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        capacities_to_add = [10]
        permission_groups = [AbakusGroup.objects.get(name='Abakus')]

        for capacity in capacities_to_add:
            pool = Pool.objects.create(
                name='Abakus', capacity=capacity, event=event,
                activation_date=(timezone.now() - timedelta(hours=24)))
            pool.permission_groups = permission_groups

        self.assertEqual(sum(capacities_to_add), event.capacity)

    def test_capacity_with_multiple_pools(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        capacities_to_add = [10, 20]
        permission_groups = [AbakusGroup.objects.get(name='Abakus')]

        for capacity in capacities_to_add:
            pool = Pool.objects.create(
                name='Abakus', capacity=capacity, event=event,
                activation_date=(timezone.now() - timedelta(hours=24)))
            pool.permission_groups = permission_groups

        self.assertEqual(sum(capacities_to_add), event.capacity)


class RegistrationTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(merge_time=timezone.now() + timedelta(hours=12))

    def test_can_register_single_pool(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        event.register(user=user, pool=pool)
        self.assertEqual(pool.number_of_registrations, event.number_of_registrations)

    def test_can_register_with_automatic_pool_selection(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Abakusmember')
        pool_2 = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        event.register(user=user)
        self.assertEqual(pool.number_of_registrations, 1)
        self.assertEqual(pool_2.number_of_registrations, 0)

    def test_no_duplicate_registrations(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(id=3)
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        self.assertEqual(pool.number_of_registrations, 0)

        event.register(user=user, pool=pool)
        event.register(user=user, pool=pool)

        self.assertEqual(pool.number_of_registrations, 1)

    def test_can_not_register_pre_activation(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        permission_groups = [AbakusGroup.objects.get(name='Webkom')]
        permission_groups[0].add_user(user)
        pool_one = Pool.objects.create(
            name='Webkom', capacity=1, event=event,
            activation_date=(timezone.now() + timedelta(hours=24)))
        event.register(user=user, pool=pool_one)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.number_of_waiting_registrations, 0)

    def test_waiting_list_if_full(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(id=3)
        people_2_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + people_2_place_in_waiting_list)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            event.register(user=user, pool=pool)

        self.assertEqual(event.waiting_list.number_of_registrations, people_2_place_in_waiting_list)
        self.assertEqual(pool.number_of_registrations, pool.capacity)
        self.assertEqual(event.number_of_registrations, pool.number_of_registrations)

    def test_number_of_waiting_registrations(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Webkom')
        people_to_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + 3)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            event.register(user=user, pool=pool)

        self.assertEqual(event.number_of_waiting_registrations, people_to_place_in_waiting_list)

    def test_can_register_pre_merge(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool_one = event.pools.get(name='Abakusmember')
        pool_two = event.pools.get(name='Webkom')
        users = get_dummy_users(2)
        user_one, user_two = users[0], users[1]
        AbakusGroup.objects.get(name='Abakus').add_user(user_one)
        AbakusGroup.objects.get(name='Abakus').add_user(user_two)

        event.register(user=user_one, pool=pool_one)
        n_registrants = pool_one.number_of_registrations
        self.assertEqual(pool_one.number_of_registrations, event.number_of_registrations)

        event.register(user=user_two, pool=pool_two)
        n_registrants += pool_two.number_of_registrations
        self.assertEqual(n_registrants, event.number_of_registrations)

    def test_can_register_post_merge(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        event.merge_time = timezone.now() - timedelta(hours=12)
        permission_groups_one = [AbakusGroup.objects.get(name='Abakus')]
        permission_groups_two = [AbakusGroup.objects.get(name='Webkom')]
        pool_one = Pool.objects.create(
            name='Abakus', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_two = Pool.objects.create(
            name='Webkom', capacity=2, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))

        users = get_dummy_users(3)
        pool_one_users = 2

        for user in users[:pool_one_users]:
            permission_groups_one[0].add_user(user)
            event.register(user=user, pool=pool_one)

        for user in users[pool_one_users:]:
            permission_groups_two[0].add_user(user)
            event.register(user=user, pool=pool_two)

        registrations = pool_one.number_of_registrations + pool_two.number_of_registrations
        self.assertEqual(registrations, event.number_of_registrations)

    def test_can_only_register_with_correct_permission_group(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        event.merge_time = timezone.now() - timedelta(hours=12)
        permission_groups_one = [AbakusGroup.objects.get(name='Abakus')]
        permission_groups_two = [AbakusGroup.objects.get(name='Webkom')]
        pool_one = Pool.objects.create(
            name='Abakus', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_one.permission_groups = permission_groups_one
        pool_two = Pool.objects.create(
            name='Webkom', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_two.permission_groups = permission_groups_two

        # Permission groups

        user = get_dummy_users(1)[0]
        permission_groups_one[0].add_user(user)
        event.register(user=user, pool=pool_one)
        event.register(user=user, pool=pool_two)

        self.assertEqual(pool_one.number_of_registrations, 1)
        self.assertEqual(pool_two.number_of_registrations, 0)

    def test_placed_in_waiting_list_post_merge(self):
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        permission_groups = [AbakusGroup.objects.get(name='Webkom')]
        pool = Pool.objects.create(
            name='Webkom', capacity=2, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool.permission_groups = permission_groups
        event.merge_time = timezone.now() - timedelta(hours=12)
        users = get_dummy_users(3)
        expected_users_in_waiting_list = 1

        for user in users:
            permission_groups[0].add_user(user)
            event.register(user, pool=pool)

        self.assertEqual(event.waiting_list.number_of_registrations, expected_users_in_waiting_list)

    def test_bump(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 2)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            event.register(user=user, pool=pool)

        waiting_list_before = event.number_of_waiting_registrations
        regs_before = event.number_of_registrations
        pool_before = pool.number_of_registrations

        event.bump(from_pool=pool)

        self.assertEqual(event.number_of_registrations, regs_before + 1)
        self.assertEqual(event.number_of_waiting_registrations, waiting_list_before - 1)
        self.assertEqual(event.waiting_list.registrations.first().user, users[3])
        self.assertEqual(pool.number_of_registrations, pool_before + 1)

    def test_unregistering_from_event(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Webkom')
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)

        with AssertInvariant(event.waiting_list):
            event.register(user=user, pool=pool)
            registrations_before = event.number_of_registrations
            event.unregister(user)

        self.assertEqual(event.number_of_registrations, registrations_before - 1)

    def test_unregistering_non_existing_user(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        with self.assertRaises(Registration.DoesNotExist):
            event.unregister(user)

    def test_popping_from_waiting_list_pre_merge(self):
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        permission_groups = [AbakusGroup.objects.get(name='Webkom')]
        pool = Pool.objects.create(
            name='Webkom', capacity=0, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool.permission_groups = permission_groups
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            permission_groups[0].add_user(user)
            event.register(user=user, pool=pool)

        prev = event.waiting_list.pop()
        while event.waiting_list.registrations.count() > 0:
            top = event.waiting_list.pop()
            self.assertLess(prev.registration_date, top.registration_date)
            prev = top

    def test_popping_from_waiting_list_post_merge(self):
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        permission_groups = [AbakusGroup.objects.get(name='Webkom')]
        pool = Pool.objects.create(
            name='Webkom', capacity=0, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool.permission_groups = permission_groups
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            permission_groups[0].add_user(user)
            event.register(user=user, pool=pool)

        prev = event.waiting_list.pop()
        while event.waiting_list.registrations.count() > 0:
            top = event.waiting_list.pop()
            self.assertLess(prev.registration_date, top.registration_date)
            prev = top

    def test_unregistering_from_waiting_list(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            event.register(user=user, pool=pool)

        event_size_before = event.number_of_registrations
        pool_size_before = pool.number_of_registrations
        waiting_list_before = event.number_of_waiting_registrations

        with AssertInvariant(event.waiting_list):
            event.unregister(users[-1])

        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(pool.number_of_registrations, pool_size_before)
        self.assertEqual(event.number_of_waiting_registrations, waiting_list_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.capacity)

    def test_unregistering_and_bumping(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            event.register(user=user, pool=pool)

        waiting_list_before = event.number_of_waiting_registrations
        event_size_before = event.number_of_registrations
        pool_size_before = pool.number_of_registrations

        with AssertInvariant(event.waiting_list):
            user_to_unregister = event.registrations.first().user
            event.unregister(user_to_unregister)

        self.assertEqual(pool.number_of_registrations, pool_size_before)
        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(event.number_of_waiting_registrations, waiting_list_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.capacity)

    def test_unregistering_and_bumping_post_merge(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        event.merge_time = timezone.now() - timedelta(hours=24)
        permission_groups_one = [AbakusGroup.objects.get(name='Abakus')]
        permission_groups_two = [AbakusGroup.objects.get(name='Webkom')]

        pool_one = Pool.objects.create(
            name='Abakus', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_one.permission_groups = permission_groups_one

        pool_two = Pool.objects.create(
            name='Webkom', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_two.permission_groups = permission_groups_two

        users = get_dummy_users(3)
        user_three = users.pop()
        AbakusGroup.objects.get(name='Webkom').add_user(user_three)
        event.register(user_three, pool=pool_two)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            event.register(user=user, pool=pool_one)

        waiting_list_before = event.number_of_waiting_registrations
        event_size_before = event.number_of_registrations
        pool_one_size_before = pool_one.number_of_registrations
        pool_two_size_before = pool_two.number_of_registrations

        user_to_unregister = pool_two.registrations.first().user

        with AssertInvariant(event.waiting_list):
            event.unregister(user_to_unregister)

        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(event.number_of_waiting_registrations, waiting_list_before - 1)
        self.assertEqual(pool_one.number_of_registrations, pool_one_size_before + 1)
        self.assertGreater(pool_one.number_of_registrations, pool_one.capacity)
        self.assertEqual(pool_two.number_of_registrations, pool_two_size_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.capacity)


class AssertInvariant:
    def __init__(self, waiting_list):
        self.registrations = waiting_list.registrations

    def assertInvariant(self):
        elements = self.registrations.all()
        if len(elements[1:]) > 1:
            prev = elements[0]
            for registration in elements[1:]:
                if prev.registration_date > registration.registration_date:
                    raise self.InvariantViolation()
                prev = registration

    def __enter__(self):
        self.assertInvariant()

    def __exit__(self, type, value, traceback):
        self.assertInvariant()

    class InvariantViolation(Exception):
        pass
