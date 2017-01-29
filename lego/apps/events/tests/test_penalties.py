from datetime import timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from lego.apps.events.models import Event, Registration
from lego.apps.users.models import AbakusGroup, Penalty
from lego.utils.test_utils import fake_time
from .utils import get_dummy_users


class PenaltyTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))

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
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
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

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
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
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
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

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 1)

    def test_waiting_list_on_three_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=3, source_event=event)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_waiting_list_on_more_than_three_penalties(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=2, source_event=event)
        Penalty.objects.create(user=user, reason='test2', weight=2, source_event=event)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
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

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
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
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
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
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
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

    number_of_calls = 80

    @mock.patch('django.utils.timezone.now',
                side_effect=[fake_time(2016, 10, 1) + timedelta(milliseconds=i)
                             for i in range(number_of_calls)])
    def test_bumped_if_penalties_expire_while_waiting(self, mock_now):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        users = get_dummy_users(5)
        penalty_one = Penalty.objects.create(user=users[0], reason='test',
                                             weight=1, source_event=event)
        Penalty.objects.create(user=users[0], reason='test', weight=2, source_event=event)
        abakus_users = users[:5]
        waiting_users = [users[0], users[4]]

        for user in abakus_users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
        for user in users:
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)

        penalty_one.created_at = mock_now() - timedelta(days=20)
        penalty_one.save()
        registration_to_unregister = Registration.objects.get(event=event, user=users[1])
        event.unregister(registration_to_unregister)

        self.assertIsNotNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)
