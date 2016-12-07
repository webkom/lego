from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from lego.apps.events.models import Event, Pool, Registration
from lego.apps.users.models import AbakusGroup, Penalty, User


def get_dummy_users(n):
    users = []

    for i in range(n):
        first_name = last_name = username = email = str(i)
        user = User(username=username, first_name=first_name, last_name=last_name, email=email)
        user.save()
        users.append(user)

    return users


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

    def test_delete_pool_with_registrations(self):
        with self.assertRaises(ValueError):
            self.pool.delete()

    def test_delete_pool_without_registrations(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        number_of_pools = len(event.pools.all())
        pool.delete()
        self.assertEqual(len(event.pools.all()), number_of_pools - 1)


class RegistrationMethodTest(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        self.registration = event.register(registration)

    def test_str(self):
        d = {
            'user': self.registration.user,
            'pool': self.registration.pool,
        }

        self.assertEqual(str(self.registration), str(d))


class PoolCapacityTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def create_pools(self, event, capacities_to_add, permission_groups):
        for capacity in capacities_to_add:
            pool = Pool.objects.create(
                name='Abakus', capacity=capacity, event=event,
                activation_date=(timezone.now() - timedelta(hours=24)))
            pool.permission_groups = permission_groups

    def test_capacity_with_single_pool(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        capacities_to_add = [10]
        self.create_pools(event, capacities_to_add, [AbakusGroup.objects.get(name='Abakus')])
        self.assertEqual(sum(capacities_to_add), event.capacity)

    def test_capacity_with_multiple_pools(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        capacities_to_add = [10, 20]
        self.create_pools(event, capacities_to_add, [AbakusGroup.objects.get(name='Abakus')])
        self.assertEqual(sum(capacities_to_add), event.capacity)


class RegistrationTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(merge_time=timezone.now() + timedelta(hours=12))
        Event.objects.all().update(heed_penalties=True)

    def tearDown(self):
        from django_redis import get_redis_connection
        get_redis_connection("default").flushall()

    def test_can_register_single_pool(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(pool.registrations.count(), event.number_of_registrations)

    def test_can_register_to_single_open_pool(self):
        users = get_dummy_users(10)
        abakus_users = users[:6]
        webkom_users = users[6:]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool_one = event.pools.get(name='Abakusmember')
        pool_two = event.pools.get(name='Webkom')

        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(pool_one.registrations.count(), 2)
        self.assertEqual(pool_two.registrations.count(), 2)
        self.assertEqual(event.number_of_registrations, 4)

    def test_can_register_with_automatic_pool_selection(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Abakusmember')
        pool_2 = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(pool.registrations.count(), 1)
        self.assertEqual(pool_2.registrations.count(), 0)

    def test_registration_picks_correct_pool(self):
        users = get_dummy_users(15)
        abakus_users = users[:10]
        webkom_users = users[10:]

        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Abakusmember')
        pool_2 = event.pools.get(name='Webkom')

        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        registration_webkom_1 = Registration.objects.get_or_create(event=event,
                                                                   user=webkom_users[0])[0]
        event.register(registration_webkom_1)

        self.assertEqual(pool.registrations.count(), 0)
        self.assertEqual(pool_2.registrations.count(), 1)

        registration_webkom_2 = Registration.objects.get_or_create(event=event,
                                                                   user=webkom_users[1])[0]
        registration_abakus = Registration.objects.get_or_create(event=event,
                                                                 user=abakus_users[0])[0]
        event.register(registration_webkom_2)
        event.register(registration_abakus)
        self.assertEqual(pool.registrations.count(), 1)
        self.assertEqual(pool_2.registrations.count(), 2)

    def test_no_duplicate_registrations(self):
        users = get_dummy_users(2)
        user_1, user_2 = users[0], users[1]
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(id=4)
        AbakusGroup.objects.get(name='Webkom').add_user(user_1)
        AbakusGroup.objects.get(name='Abakus').add_user(user_2)
        self.assertEqual(pool.registrations.count(), 0)

        registration_one = Registration.objects.get_or_create(event=event,
                                                              user=user_1)[0]
        event.register(registration_one)
        pool_two = Pool.objects.create(name='test', capacity=1, event=event,
                                       activation_date=(timezone.now() - timedelta(hours=24)))
        with self.assertRaises(ValueError):
            event.register(registration_one)

        self.assertEqual(event.number_of_registrations, 1)
        self.assertEqual(pool.registrations.count(), 1)
        self.assertEqual(pool_two.registrations.count(), 0)

    def test_can_not_register_pre_activation(self):
        user = get_dummy_users(1)[0]
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        permission_groups = [AbakusGroup.objects.get(name='Webkom')]
        permission_groups[0].add_user(user)
        Pool.objects.create(
            name='Webkom', capacity=1, event=event,
            activation_date=(timezone.now() + timedelta(hours=24)))
        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.waiting_registrations.count(), 0)

    def test_waiting_list_if_full(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(id=3)
        people_2_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + people_2_place_in_waiting_list)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(), people_2_place_in_waiting_list)
        self.assertEqual(pool.registrations.count(), pool.capacity)
        self.assertEqual(event.number_of_registrations, pool.registrations.count())

    def test_number_of_waiting_registrations(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Abakusmember')
        people_to_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + 3)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(),
                         people_to_place_in_waiting_list)

    def test_can_register_pre_merge(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool_one = event.pools.get(name='Abakusmember')
        pool_two = event.pools.get(name='Webkom')
        users = get_dummy_users(2)
        user_one, user_two = users[0], users[1]
        AbakusGroup.objects.get(name='Abakus').add_user(user_one)
        AbakusGroup.objects.get(name='Webkom').add_user(user_two)
        registration_one = Registration.objects.get_or_create(event=event,
                                                              user=user_one)[0]
        event.register(registration_one)
        n_registrants = pool_one.registrations.count()
        self.assertEqual(pool_one.registrations.count(), event.number_of_registrations)

        registration_two = Registration.objects.get_or_create(event=event,
                                                              user=user_two)[0]
        event.register(registration_two)
        n_registrants += pool_two.registrations.count()
        self.assertEqual(n_registrants, event.number_of_registrations)

    def test_can_register_post_merge(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        event.merge_time = timezone.now() - timedelta(hours=12)
        permission_groups_one = [AbakusGroup.objects.get(name='Abakus')]
        permission_groups_two = [AbakusGroup.objects.get(name='Webkom')]
        pool_one = Pool.objects.create(
            name='Abakus', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_one.permission_groups.add(permission_groups_one[0])
        pool_two = Pool.objects.create(
            name='Webkom', capacity=2, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool_two.permission_groups.add(permission_groups_two[0])

        users = get_dummy_users(3)

        for user in users:
            permission_groups_one[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(pool_one.registrations.count(), 3)
        self.assertEqual(pool_one.registrations.count(), event.number_of_registrations)

    def test_can_only_register_with_correct_permission_group(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        event.merge_time = timezone.now() - timedelta(hours=12)
        permission_groups_one = [AbakusGroup.objects.get(name='Abakus')]
        permission_groups_two = [AbakusGroup.objects.get(name='Webkom')]
        pool = Pool.objects.create(
            name='Webkom', capacity=1, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool.permission_groups = permission_groups_two

        user = get_dummy_users(1)[0]
        permission_groups_one[0].add_user(user)

        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(pool.registrations.count(), 0)

    def test_placed_in_waiting_list_post_merge(self):
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        permission_groups = [AbakusGroup.objects.get(name='Webkom')]
        pool = Pool.objects.create(
            name='Webkom', capacity=2, event=event,
            activation_date=(timezone.now() - timedelta(hours=24)))
        pool.permission_groups = permission_groups
        event.merge_time = timezone.now() - timedelta(hours=12)
        users = get_dummy_users(pool.capacity + 1)
        expected_users_in_waiting_list = 1

        for user in users:
            permission_groups[0].add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(event.waiting_registrations.count(), expected_users_in_waiting_list)

    def test_bump(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 2)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        waiting_list_before = event.waiting_registrations.count()
        regs_before = event.number_of_registrations
        pool_before = pool.registrations.count()

        event.bump(to_pool=pool)

        self.assertEqual(event.number_of_registrations, regs_before + 1)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertEqual(event.waiting_registrations.first().user, users[4])
        self.assertEqual(pool.registrations.count(), pool_before + 1)

    def test_unregistering_from_event(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Webkom')
        users = get_dummy_users(5)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        AbakusGroup.objects.get(name='Webkom').add_user(users[0])

        registration = Registration.objects.get_or_create(event=event,
                                                          user=users[0])[0]
        event.register(registration)
        registrations_before = event.number_of_registrations
        pool_registrations_before = pool.registrations.count()
        event.unregister(registration)

        self.assertEqual(event.number_of_registrations, registrations_before - 1)
        self.assertEqual(pool.registrations.count(), pool_registrations_before - 1)

    def test_register_after_unregister(self):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        registrations_before = event.number_of_registrations

        registration = Registration.objects.get(event=event, user=user)
        event.unregister(registration)
        self.assertEqual(event.number_of_registrations, registrations_before - 1)

        event.register(registration)
        self.assertEqual(event.number_of_registrations, registrations_before)

    def test_register_to_waiting_list_after_unregister(self):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(event.waiting_registrations.count(), 1)

        event.unregister(registration)
        self.assertEqual(event.waiting_registrations.count(), 0)

        event.register(registration)
        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_unregistering_non_existing_user(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        with self.assertRaises(Registration.DoesNotExist):
            registration = Registration.objects.get(event=event, user=user)
            event.unregister(registration)

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
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        prev = event.pop_from_waiting_list()
        for top in event.waiting_registrations:
            self.assertLessEqual(prev.registration_date, top.registration_date)
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
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        prev = event.pop_from_waiting_list()
        for registration in event.waiting_registrations:
            self.assertLessEqual(prev.registration_date, registration.registration_date)
            prev = registration

    def test_unregistering_from_waiting_list(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        event_size_before = event.number_of_registrations
        pool_size_before = pool.registrations.count()
        waiting_list_before = event.waiting_registrations.count()

        registration_last = Registration.objects.get(event=event, user=users[-1])
        event.unregister(registration_last)

        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(pool.registrations.count(), pool_size_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.capacity)

    def test_unregistering_and_bumping(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.first()
        users = get_dummy_users(pool.capacity + 10)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        waiting_list_before = event.waiting_registrations.count()
        event_size_before = event.number_of_registrations
        pool_size_before = pool.registrations.count()

        user_to_unregister = event.registrations.first().user
        registration_to_unregister = Registration.objects.get(event=event, user=user_to_unregister)
        event.unregister(registration_to_unregister)

        self.assertEqual(pool.registrations.count(), pool_size_before)
        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.capacity)

    def test_unregistering_and_bumping_post_merge(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.merge_time = timezone.now() - timedelta(hours=24)
        event.save()
        pool_one = event.pools.get(name='Abakusmember')
        pool_two = event.pools.get(name='Webkom')

        users = get_dummy_users(6)
        abakus_users = users[:3]
        webkom_users = users[3:5]

        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            event.admin_register(user, pool_one)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            event.admin_register(user, pool_two)

        AbakusGroup.objects.get(name='Abakus').add_user(users[5])
        registration = Registration.objects.get_or_create(event=event,
                                                          user=users[5])[0]
        event.register(registration)

        waiting_list_before = event.waiting_registrations.count()
        event_size_before = event.number_of_registrations
        pool_one_size_before = pool_one.registrations.count()
        pool_two_size_before = pool_two.registrations.count()

        user_to_unregister = pool_two.registrations.first().user
        registration_to_unregister = Registration.objects.get(event=event, user=user_to_unregister)

        event.unregister(registration_to_unregister)

        self.assertEqual(event.number_of_registrations, event_size_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before - 1)
        self.assertEqual(pool_one.registrations.count(), pool_one_size_before + 1)
        self.assertGreater(pool_one.registrations.count(), pool_one.capacity)
        self.assertEqual(pool_two.registrations.count(), pool_two_size_before - 1)
        self.assertLessEqual(event.number_of_registrations, event.capacity)

    def test_bumping_when_bumped_has_several_pools_available(self):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        users = get_dummy_users(4)
        user_0 = users[0]
        pre_reg = event.registrations.first()
        pool = event.pools.get(name='Webkom')

        pool_registrations_before = pool.registrations.count()
        waiting_list_before = event.waiting_registrations.count()
        number_of_registered_before = event.number_of_registrations

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertEqual(pool.registrations.count(), pool_registrations_before + 3)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before + 1)
        self.assertEqual(event.number_of_registrations, number_of_registered_before + 3)

        event.unregister(pre_reg)

        self.assertEqual(pool.registrations.count(), pool_registrations_before + 3)
        self.assertEqual(event.waiting_registrations.count(), waiting_list_before)
        self.assertEqual(event.number_of_registrations, number_of_registered_before + 3)

        registration_to_unregister = Registration.objects.get(event=event, user=user_0)
        event.unregister(registration_to_unregister)

        self.assertEqual(event.number_of_registrations, number_of_registered_before + 2)

    def test_unregistration_date_is_set_at_unregistration(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        registration = event.registrations.first()

        self.assertIsNone(registration.unregistration_date)
        event.unregister(registration)
        registration = event.registrations.first()
        self.assertIsNotNone(registration.unregistration_date)

    def test_bump_after_rebalance(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool_one = event.pools.get(name='Abakusmember')
        pool_two = event.pools.get(name='Webkom')
        users = get_dummy_users(6)
        abakus_users = users[0:3]
        webkom_users = users[3:6]
        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)
        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        pool_one_before = pool_one.registrations.count()
        pool_two_before = pool_two.registrations.count()
        waiting_before = event.waiting_registrations.count()

        registration_to_unregister = Registration.objects.get(event=event, user=webkom_users[0])
        event.unregister(registration_to_unregister)
        self.assertEqual(pool_one.registrations.count(), pool_one_before)
        self.assertEqual(pool_two.registrations.count(), pool_two_before)
        self.assertEqual(event.waiting_registrations.count(), waiting_before - 1)

    def test_user_is_moved_after_rebalance(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool_one = event.pools.get(name='Abakusmember')
        pool_two = event.pools.get(name='Webkom')
        users = get_dummy_users(6)
        abakus_users = users[0:3]
        webkom_users = users[3:6]
        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)
        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        moved_user_registration = event.registrations.get(user=webkom_users[2])
        self.assertEqual(moved_user_registration.pool, pool_one)

        registration_to_unregister = Registration.objects.get(event=event, user=webkom_users[0])
        event.unregister(registration_to_unregister)
        moved_user_registration = event.registrations.get(user=webkom_users[2])
        self.assertEqual(moved_user_registration.pool, pool_two)

    def test_correct_user_is_bumped_after_rebalance(self):
        # Correct as in first user available for the rebalanced pool
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool_one = event.pools.get(name='Abakusmember')
        users = get_dummy_users(7)
        abakus_users = users[0:4]
        webkom_users = users[4:7]
        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        for user in webkom_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)
        for user in abakus_users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        waiting_before = event.waiting_registrations.count()
        user_to_be_bumped = event.waiting_registrations.get(user=abakus_users[2]).user
        user_not_to_be_bumped = event.waiting_registrations.get(user=abakus_users[3]).user

        registration_to_unregister = Registration.objects.get(event=event, user=webkom_users[0])
        event.unregister(registration_to_unregister)
        self.assertEqual(event.registrations.get(user=user_to_be_bumped).pool, pool_one)
        self.assertIsNone(event.registrations.get(user=user_not_to_be_bumped).pool)
        self.assertEqual(event.waiting_registrations.count(), waiting_before - 1)

    def test_doesnt_have_pool_permission(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        self.assertFalse(event.has_pool_permission(user, abakus_pool))
        self.assertFalse(event.has_pool_permission(user, webkom_pool))

    def test_has_some_pool_permissions(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        self.assertTrue(event.has_pool_permission(user, abakus_pool))
        self.assertFalse(event.has_pool_permission(user, webkom_pool))

    def test_has_all_pool_permissions(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        self.assertTrue(event.has_pool_permission(user, abakus_pool))
        self.assertTrue(event.has_pool_permission(user, webkom_pool))

    def test_rebalance_pool_method(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        users = get_dummy_users(4)
        abakus_user = users[0]
        webkom_users = users[1:]
        AbakusGroup.objects.get(name='Abakus').add_user(abakus_user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        registration_abakus = Registration.objects.get_or_create(event=event,
                                                                 user=abakus_user)[0]
        event.register(registration_abakus)
        for user in webkom_users[:2]:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertFalse(event.rebalance_pool(abakus_pool, webkom_pool))
        self.assertEqual(abakus_pool.registrations.count(), 1)
        self.assertEqual(webkom_pool.registrations.count(), 2)

        registration_webkom = Registration.objects.get_or_create(event=event,
                                                                 user=webkom_users[2])[0]
        event.register(registration_webkom)

        registration_to_unregister = Registration.objects.get(event=event, user=webkom_users[0])
        event.unregister(registration_to_unregister)
        self.assertEqual(abakus_pool.registrations.count(), 2)
        self.assertEqual(webkom_pool.registrations.count(), 1)

        self.assertTrue(event.rebalance_pool(abakus_pool, webkom_pool))
        self.assertEqual(abakus_pool.registrations.count(), 1)
        self.assertEqual(webkom_pool.registrations.count(), 2)

    def test_calculate_full_pools(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        users = get_dummy_users(5)
        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)

        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 0)
        self.assertEqual(len(open_pools), 2)

        for user in users[:3]:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)
        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 1)
        self.assertEqual(len(open_pools), 1)

        for user in users[3:]:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)
        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 2)
        self.assertEqual(len(open_pools), 0)

    def test_find_most_exclusive_pool(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')

        users = get_dummy_users(3)
        user_three = users.pop()
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        AbakusGroup.objects.get(name='Webkom').add_user(user_three)

        self.assertEqual(event.find_most_exclusive_pools(
            [webkom_pool, abakus_pool])[0], webkom_pool)
        self.assertEqual(len(event.find_most_exclusive_pools([webkom_pool, abakus_pool])), 1)

    def test_find_most_exclusive_when_equal(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')
        users = get_dummy_users(3)
        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
        self.assertEqual(len(event.find_most_exclusive_pools([webkom_pool, abakus_pool])), 2)

    def test_select_highest_capacity(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')
        self.assertEqual(event.select_highest_capacity([abakus_pool, webkom_pool]), abakus_pool)

    def test_get_earliest_registration_time_no_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')

        current_time = timezone.now()
        webkom_pool.activation_date = current_time
        webkom_pool.save()
        abakus_pool.activation_date = current_time-timedelta(hours=1)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)

        earliest_reg = event.get_earliest_registration_time(user, [webkom_pool, abakus_pool])
        self.assertEqual(earliest_reg, current_time-timedelta(hours=1))

    def test_get_earliest_registration_time_ignore_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.heed_penalties = False
        event.save()

        current_time = timezone.now()
        webkom_pool = event.pools.get(name='Webkom')
        webkom_pool.activation_date = current_time
        webkom_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=1, source_event=event)
        penalties = user.number_of_penalties()

        earliest_reg = event.get_earliest_registration_time(user, [webkom_pool], penalties)
        self.assertEqual(earliest_reg, current_time)

    def test_get_earliest_registration_time_one_penalty(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        current_time = timezone.now()
        webkom_pool = event.pools.get(name='Webkom')
        webkom_pool.activation_date = current_time
        webkom_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=1, source_event=event)
        penalties = user.number_of_penalties()

        earliest_reg = event.get_earliest_registration_time(user, [webkom_pool], penalties)
        self.assertEqual(earliest_reg, current_time + timedelta(hours=3))

    def test_get_earliest_registration_time_two_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        current_time = timezone.now()
        webkom_pool = event.pools.get(name='Webkom')
        webkom_pool.activation_date = current_time
        webkom_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=2, source_event=event)
        penalties = user.number_of_penalties()

        earliest_reg = event.get_earliest_registration_time(user, [webkom_pool], penalties)
        self.assertEqual(earliest_reg, current_time + timedelta(hours=12))

    def test_cant_register_with_one_penalty_before_delay(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        current_time = timezone.now()
        abakus_pool = event.pools.get(name='Abakusmember')
        abakus_pool.activation_date = current_time
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=1, source_event=event)

        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

    def test_can_register_with_one_penalty_after_delay(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        current_time = timezone.now()
        abakus_pool = event.pools.get(name='Abakusmember')
        abakus_pool.activation_date = current_time - timedelta(hours=3)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=1, source_event=event)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 1)

    def test_cant_register_with_two_penalties_before_delay(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        current_time = timezone.now()
        abakus_pool = event.pools.get(name='Abakusmember')
        abakus_pool.activation_date = current_time
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=2, source_event=event)

        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

    def test_can_register_with_two_penalties_after_delay(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        current_time = timezone.now()
        abakus_pool = event.pools.get(name='Abakusmember')
        abakus_pool.activation_date = current_time - timedelta(hours=12)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=2, source_event=event)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 1)

    def test_waiting_list_on_three_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=3, source_event=event)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_waiting_list_on_three_penalties_post_merge(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.merge_time = timezone.now() - timedelta(hours=24)
        event.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=3, source_event=event)

        registration = Registration.objects.get_or_create(event=event,
                                                          user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_not_bumped_if_three_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        users = get_dummy_users(5)
        abakus_users = users[:5]
        waiting_users = users[3:5]

        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)

        Penalty.objects.create(user=waiting_users[0], reason='test', weight=3, source_event=event)
        registration_to_unregister = Registration.objects.get(event=event, user=users[0])
        event.unregister(registration_to_unregister)

        self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNotNone(event.registrations.get(user=waiting_users[1]).pool)

    def test_not_bumped_if_three_penalties_post_merge(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        users = get_dummy_users(7)
        abakus_users = users[:5]
        webkom_users = users[5:7]
        waiting_users = users[3:5]

        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in webkom_users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
        for user in users:
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)

        event.merge_time = timezone.now() - timedelta(hours=24)
        event.save()
        Penalty.objects.create(user=waiting_users[0], reason='test', weight=3, source_event=event)

        registration_to_unregister = Registration.objects.get(event=event, user=webkom_users[0])
        event.unregister(registration_to_unregister)

        self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNotNone(event.registrations.get(user=waiting_users[1]).pool)

    def test_bumped_if_penalties_expire_while_waiting(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        users = get_dummy_users(5)
        dt = timezone.datetime(2016, 10, 1)
        dt = timezone.pytz.timezone('UTC').localize(dt)
        with mock.patch('django.utils.timezone.now', return_value=dt):
            penalty_one = Penalty.objects.create(user=users[0], reason='test',
                                                 weight=1, source_event=event)
            Penalty.objects.create(user=users[0], reason='test', weight=2, source_event=event)
            abakus_users = users[:5]
            waiting_users = [users[0], users[4]]

            for user in abakus_users:
                AbakusGroup.objects.get(name='Abakus').add_user(user)
            for user in users:
                registration = Registration.objects.get_or_create(event=event,
                                                                  user=user)[0]
                event.register(registration)

            self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
            self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)

            penalty_one.created_at = timezone.now() - timedelta(days=20)
            penalty_one.save()
            registration_to_unregister = Registration.objects.get(event=event, user=users[1])
            event.unregister(registration_to_unregister)

            self.assertIsNotNone(event.registrations.get(user=waiting_users[0]).pool)
            self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)


class AdminRegistrationTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(merge_time=timezone.now() + timedelta(hours=12))

    def test_admin_registration(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.first()

        no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, no_of_regs_before + 1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before + 1)

    def test_ar_with_wrong_pool(self):
        event_one = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        event_two = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        wrong_pool = event_two.pools.first()

        e1_no_of_regs_before = event_one.number_of_registrations
        e2_no_of_regs_before = event_two.number_of_registrations
        pool_no_of_regs_before = wrong_pool.registrations.count()

        with self.assertRaises(ValueError):
            event_one.admin_register(user, wrong_pool)
        self.assertEqual(event_one.number_of_registrations, e1_no_of_regs_before)
        self.assertEqual(event_two.number_of_registrations, e2_no_of_regs_before)
        self.assertEqual(wrong_pool.registrations.count(), pool_no_of_regs_before)

    def test_ar_without_permissions_for_user(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before+1)

    def test_ar_after_merge(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.merge_time = timezone.now() - timedelta(hours=12)
        user = get_dummy_users(1)[0]
        pool = event.pools.first()

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before+1)

    def test_ar_to_full_pool(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        users = get_dummy_users(5)
        user = users[4]
        for u in users[:4]:
            AbakusGroup.objects.get(name='Abakus').add_user(u)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=u)[0]
            event.register(registration)
        pool = event.pools.first()

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before+1)

    def test_ar_to_full_event(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        users = get_dummy_users(7)
        user = users[6]
        for u in users[:6]:
            AbakusGroup.objects.get(name='Webkom').add_user(u)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=u)[0]
            event.register(registration)
        pool = event.pools.first()

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before+1)

    def test_ar_twice(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        e1_no_of_regs_before = event.number_of_registrations

        event.admin_register(user, pool)
        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)


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
