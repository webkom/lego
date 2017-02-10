from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tasks import async_register, check_events_for_bumps
from lego.apps.events.tests.test_events_api import _get_pools_list_url
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.models import AbakusGroup, Penalty, User
from lego.utils.test_utils import fake_time


class PoolActivationTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    _test_pools_data = [
        {
            'name': 'TESTPOOL1',
            'capacity': 2,
            'activation_date': timezone.now(),
            'permission_groups': [1]
        },
    ]

    def setUp(self):
        self.event = Event.objects.get(title='NO_POOLS_ABAKUS')
        self.event.start_time = timezone.now() + timedelta(hours=12)
        self.event.save()
        self.pool = Pool.objects.create(
            name='test', capacity=1, event=self.event,
            activation_date=(timezone.now() - timedelta(hours=24))
        )
        self.pool.permission_groups = [AbakusGroup.objects.get(name='Abakus')]
        self.pool.save()

    def tearDown(self):
        from django_redis import get_redis_connection
        get_redis_connection("default").flushall()

    def create_pool_through_api(self, test_pool_index):
        pool_user = User.objects.first()
        AbakusGroup.objects.get(name='Webkom').add_user(pool_user)
        self.client.force_authenticate(pool_user)
        pool_response = self.client.post(_get_pools_list_url(
            self.event.id), self._test_pools_data[test_pool_index]
        )
        return Pool.objects.get(id=pool_response.data.get('id', None))

    def test_user_is_bumped_upon_pool_activation(self):
        """" Tests that a waiting user is bumped when a new pool is activated """
        users = get_dummy_users(2)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event,
                                                              user=user)[0]
            self.event.register(registration)

        new_pool = self.create_pool_through_api(0)
        self.assertEqual(new_pool.registrations.count(), 1)

    def test_several_users_are_bumped_upon_pool_activation(self):
        """ Tests that we can bump several users (2) to a new pool. """
        users = get_dummy_users(3)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event,
                                                              user=user)[0]
            self.event.register(registration)

        new_pool = self.create_pool_through_api(0)
        self.assertEqual(new_pool.registrations.count(), 2)

    def test_too_many_users_waiting_for_bump(self):
        """ Tests that only 2 users are bumped to a new pool with capacity = 2. """
        users = get_dummy_users(4)
        registrations = []

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event,
                                                              user=user)[0]
            self.event.register(registration)
            registrations.append(Registration.objects.get(id=registration.id))

        new_pool = self.create_pool_through_api(0)
        self.assertEqual(new_pool.registrations.count(), 2)
        self.assertIsNone(registrations[3].pool)


class PenaltyExpiredTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        self.event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.event.heed_penalties = True

        self.event.save()

    def tearDown(self):
        from django_redis import get_redis_connection
        get_redis_connection("default").flushall()

    def mocked_setup(self, mock_now):
        self.event.start_time = mock_now() + timedelta(days=1)
        self.event.merge_time = mock_now() + timedelta(hours=12)
        self.event.save()
        for pool in self.event.pools.all():
            pool.activation_time = mock_now() - timedelta(days=1)
            pool.capacity = 1
            pool.save()

    def expiration_offset(self, mock_calls_at_expiration, mock_calls_at_penalty_creation):
        twenty_days = timedelta(days=20)
        expiration = timedelta(milliseconds=mock_calls_at_expiration)
        penalty_creation = timedelta(milliseconds=mock_calls_at_penalty_creation)
        return twenty_days - expiration + penalty_creation

    number_of_calls = 43

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_is_automatically_bumped_after_penalty_expiration(self, mock_now):
        """ Tests that a task for automatic bump is created if user has 3 penalties,
            and that the user is bumped when they expire"""
        self.mocked_setup(mock_now)

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        Penalty.objects.create(
            user=user,
            reason='test',
            weight=3,
            source_event=self.event,
            created_at=mock_now()-self.expiration_offset(22, 7)
        )

        registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
        async_register(registration.id)
        check_events_for_bumps.delay()
        self.assertIsNotNone(Registration.objects.get(id=registration.id).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    number_of_calls = 43

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_is_bumped_with_multiple_penalties(self, mock_now):
        """ Tests that a user is bumped when going from 4 to 2 active penalties"""
        self.mocked_setup(mock_now)

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        Penalty.objects.create(
            user=user,
            reason='test',
            weight=2,
            source_event=self.event,
            created_at=mock_now()-self.expiration_offset(24, 8)
        )

        Penalty.objects.create(
            user=user,
            reason='test2',
            weight=2,
            source_event=self.event,
            created_at=mock_now()
        )

        registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
        async_register(registration.id)
        check_events_for_bumps.delay()
        self.assertIsNotNone(Registration.objects.get(id=registration.id).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    number_of_calls = 29

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_isnt_bumped_with_too_many_penalties(self, mock_now):
        """ Tests that a user isn't bumped when going from 4 to 3 active penalties """
        self.mocked_setup(mock_now)

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        Penalty.objects.create(
            user=user,
            reason='test',
            weight=1,
            source_event=self.event,
            created_at=mock_now()-self.expiration_offset(24, 8)
        )

        Penalty.objects.create(
            user=user,
            reason='test2',
            weight=3,
            source_event=self.event,
            created_at=mock_now()
        )

        registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
        async_register(registration.id)
        check_events_for_bumps.delay()
        self.assertIsNone(Registration.objects.get(id=registration.id).pool)
        self.assertEqual(self.event.number_of_registrations, 0)

    number_of_calls = 43

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_isnt_bumped_when_full(self, mock_now):
        """ Tests that a user isnt bumped when the event is full when penalties expire. """
        self.mocked_setup(mock_now)

        users = get_dummy_users(2)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)

        Penalty.objects.create(
            user=users[1],
            reason='test',
            weight=3,
            source_event=self.event,
            created_at=mock_now()-self.expiration_offset(35, 12)
        )

        for user in users:
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            async_register(registration.id)

        check_events_for_bumps.delay()

        self.assertIsNone(Registration.objects.get(user=users[1]).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    number_of_calls = 63

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_isnt_bumped_when_not_first_in_line(self, mock_now):
        """ Tests that a user isnt bumped when not first in the waiting list.
            In practice, this should never happen, because the only reason someone
            is in front of you in the list is if the event is full, which is tested above.
        """
        self.mocked_setup(mock_now)

        users = get_dummy_users(3)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)

        Penalty.objects.create(
            user=users[2],
            reason='test',
            weight=3,
            source_event=self.event,
            created_at=mock_now()-self.expiration_offset(48, 14)
        )

        for user in users:
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            async_register(registration.id)
        check_events_for_bumps.delay()

        self.assertIsNone(Registration.objects.get(user=users[1]).pool)
        self.assertIsNone(Registration.objects.get(user=users[2]).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    number_of_calls = 63

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_async_bump_post_merge(self, mock_now):
        """ Tests that a waiting user with penalties is bumped to any pool after merge"""
        self.mocked_setup(mock_now)
        self.event.merge_time = mock_now()
        self.event.save()

        users = get_dummy_users(2)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)

        Penalty.objects.create(
            user=users[1],
            reason='test',
            weight=3,
            source_event=self.event,
            created_at=mock_now()-self.expiration_offset(40, 12)
        )

        for user in users:
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            async_register(registration.id)
        check_events_for_bumps.delay()

        self.assertIsNotNone(Registration.objects.get(user=users[1]).pool)
        self.assertEqual(self.event.number_of_registrations, 2)
