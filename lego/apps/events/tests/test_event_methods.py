from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from lego.apps.events.models import Event, Registration, Pool
from lego.apps.users.models import AbakusGroup

from .utils import get_dummy_users


class EventMethodTest(TestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))

    def test_str(self):
        event = Event.objects.get(pk=1)
        self.assertEqual(str(event), event.title)

    def test_calculate_full_pools(self):
        """Test calculation of open and full pools for usage in registering method"""
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
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 1)
        self.assertEqual(len(open_pools), 1)

        for user in users[3:]:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)
        full_pools, open_pools = event.calculate_full_pools([abakus_pool, webkom_pool])
        self.assertEqual(len(full_pools), 2)
        self.assertEqual(len(open_pools), 0)

    def test_doesnt_have_pool_permission(self):
        """Test method checking that user does not have the appropriate permission groups"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        self.assertFalse(event.has_pool_permission(user, abakus_pool))
        self.assertFalse(event.has_pool_permission(user, webkom_pool))

    def test_has_some_pool_permissions(self):
        """Test method checking that user one of the appropriate permission groups"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        self.assertTrue(event.has_pool_permission(user, abakus_pool))
        self.assertFalse(event.has_pool_permission(user, webkom_pool))

    def test_has_all_pool_permissions(self):
        """Test method checking that user have all the appropriate permission groups"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        abakus_pool = event.pools.get(name='Abakusmember')
        webkom_pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        self.assertTrue(event.has_pool_permission(user, abakus_pool))
        self.assertTrue(event.has_pool_permission(user, webkom_pool))

    def test_find_most_exclusive_pool(self):
        """Test method calculating the most exclusive pool for the registering user"""
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
        """Test method calculating the most exclusive pool when they are equally exclusive"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')
        users = get_dummy_users(3)
        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
        self.assertEqual(len(event.find_most_exclusive_pools([webkom_pool, abakus_pool])), 2)

    def test_select_highest_capacity(self):
        """Test method selecting the pool with the highest capacity"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')
        self.assertEqual(event.select_highest_capacity([abakus_pool, webkom_pool]), abakus_pool)

    def test_get_earliest_registration_time_without_pools_provided(self):
        """Test method calculating the earliest registration time for user without provided pools"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')

        current_time = timezone.now()
        webkom_pool.activation_date = current_time
        webkom_pool.save()
        abakus_pool.activation_date = current_time - timedelta(hours=1)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)
        earliest_reg = event.get_earliest_registration_time(user)

        self.assertEqual(earliest_reg, abakus_pool.activation_date)

    def test_get_earliest_registration_time_no_penalties(self):
        """Test method calculating the earliest registration time for two pools"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        webkom_pool = event.pools.get(name='Webkom')
        abakus_pool = event.pools.get(name='Abakusmember')

        current_time = timezone.now()
        webkom_pool.activation_date = current_time
        webkom_pool.save()
        abakus_pool.activation_date = current_time - timedelta(hours=1)
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)

        earliest_reg = event.get_earliest_registration_time(user, [webkom_pool, abakus_pool])
        self.assertEqual(earliest_reg, current_time-timedelta(hours=1))

    def test_number_of_waiting_registrations(self):
        """Test method counting the number of registrations in waiting list"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        pool = event.pools.get(name='Abakusmember')
        people_to_place_in_waiting_list = 3
        users = get_dummy_users(pool.capacity + 3)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(
            event.waiting_registrations.count(), people_to_place_in_waiting_list
        )

    def test_spots_left_for_user_before_merge(self):
        """Test that spots_left_for_user returns correct number of spots"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        pool = event.pools.get(name='Abakusmember')
        pool.capacity = 10
        pool.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        self.assertEqual(event.spots_left_for_user(user), 8)

    def test_spots_left_for_user_before_merge_multiple_pools(self):
        """Test that spots_left_for_user returns correct number of spots with multiple pools"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        pool = event.pools.get(name='Abakusmember')
        pool.capacity = 10
        pool.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Webkom').add_user(user)

        self.assertEqual(event.spots_left_for_user(user), 11)

    def test_spots_left_for_user_after_merge(self):
        """Test that spots_left_for_user returns correct number of spots after merge"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        event.merge_time = timezone.now() - timedelta(days=1)
        event.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        self.assertEqual(event.spots_left_for_user(user), 3)

    def test_is_full_when_not_full(self):
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        self.assertEqual(event.is_full, False)

    def test_is_full_when_full(self):
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        users = get_dummy_users(5)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.is_full, True)

    def test_is_full_when_unlimited(self):

        event = Event.objects.get(title="NO_POOLS_ABAKUS")

        pool = Pool.objects.create(
            name="Pool1", event=event, capacity=0,
            activation_date=timezone.now() - timedelta(days=1)
        )
        webkom_group = AbakusGroup.objects.get(name='Webkom')
        pool.permission_groups.set([webkom_group])
        users = get_dummy_users(5)

        for user in users:
            webkom_group.add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertEqual(event.is_full, False)
