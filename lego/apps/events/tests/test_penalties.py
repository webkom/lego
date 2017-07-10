from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from lego.apps.events.models import Event, Registration
from lego.apps.users.models import AbakusGroup, Penalty

from .utils import get_dummy_users


class PenaltyTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))

    def test_get_earliest_registration_time_ignore_penalties(self):
        """Test method calculating the earliest registration time when penalties are ignored"""
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
        """Test method calculating the earliest registration time for user with one penalty"""
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
        """Test method calculating the earliest registration time for user with two penalties"""
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
        """Test that user can not register before (3 hour) delay when having one penalty"""
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
        """Test that user can register after (3 hour) delay has passed having one penalty"""
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
        """Test that user can not register before (12 hour) delay when having two penalties"""
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
        """Test that user can register after (12 hour) delay when having two penalties"""
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
        """Test that user is registered to waiting list directly when having three penalties"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)
        Penalty.objects.create(user=user, reason='test', weight=3, source_event=event)

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 0)
        self.assertEqual(event.waiting_registrations.count(), 1)

    def test_waiting_list_on_more_than_three_penalties(self):
        """Test that user is registered to waiting list directly having over three penalties"""
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
        """Test that user is registered to waiting list with three penalties after merge"""
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
        """Test that user is not bumped on unregistration having three penalties"""
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
        """Test that user is not bumped on unregistration having three penalties after merge"""
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

    def test_bumped_if_penalties_expire_while_waiting(self):
        """Test that user gets bumped when penalties expire while on waiting list"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')

        for pool in event.pools.all():
            pool.activation_date = timezone.now() - timedelta(hours=12)
            pool.save()

        users = get_dummy_users(5)
        penalty_one = Penalty.objects.create(
            user=users[0], reason='test', weight=1, source_event=event
        )
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

        penalty_one.created_at = timezone.now() - timedelta(days=365)
        penalty_one.save()
        registration_to_unregister = Registration.objects.get(event=event, user=users[1])
        event.unregister(registration_to_unregister)

        self.assertIsNotNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNone(event.registrations.get(user=waiting_users[1]).pool)

    def test_isnt_bumped_if_third_penalty_expires_but_reg_delay_is_still_active(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        for pool in event.pools.all():
            pool.activation_date = timezone.now() - timedelta(hours=6)
            pool.save()

        users = get_dummy_users(5)
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

        penalty_one.created_at = timezone.now() - timedelta(days=365)
        penalty_one.save()
        registration_to_unregister = Registration.objects.get(event=event, user=users[1])
        event.unregister(registration_to_unregister)

        self.assertIsNone(event.registrations.get(user=waiting_users[0]).pool)
        self.assertIsNotNone(event.registrations.get(user=waiting_users[1]).pool)

    def test_no_legal_bump(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        users = get_dummy_users(5)
        for pool in event.pools.all():
            pool.activation_date = timezone.now()
            pool.save()

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=event,
                                                              user=user)[0]
            event.register(registration)

        self.assertIsNone(event.registrations.get(user=users[3]).pool)
        self.assertIsNone(event.registrations.get(user=users[4]).pool)

        Penalty.objects.create(user=users[3], reason='test', weight=3, source_event=event)
        Penalty.objects.create(user=users[4], reason='test', weight=2, source_event=event)

        registration_to_unregister = Registration.objects.get(event=event, user=users[0])
        event.unregister(registration_to_unregister)

        self.assertIsNone(event.registrations.get(user=users[3]).pool)
        self.assertIsNone(event.registrations.get(user=users[4]).pool)

    def test_penalties_created_on_unregister(self):
        """Test that user gets penalties on unregister after limit"""
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        for pool in event.pools.all():
            pool.unregistration_deadline = timezone.now() - timedelta(days=1)
            pool.save()

        registration = event.registrations.first()
        penalties_before = len(registration.user.penalties.all())

        event.unregister(registration)

        penalties_after = len(registration.user.penalties.all())
        self.assertGreater(penalties_after, penalties_before)
        self.assertEqual(penalties_after, 1)
