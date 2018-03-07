from datetime import timedelta
from unittest import mock

from django.utils import timezone

from lego.apps.events import constants
from lego.apps.events.exceptions import PoolCounterNotEqualToRegistrationCount
from lego.apps.events.models import Event, Registration
from lego.apps.events.tasks import (
    async_register, bump_waiting_users_to_new_pool,
    check_events_for_registrations_with_expired_penalties,
    check_that_pool_counters_match_registration_number, notify_event_creator_when_payment_overdue,
    notify_user_when_payment_soon_overdue
)
from lego.apps.events.tests.utils import get_dummy_users, make_penalty_expire
from lego.apps.users.models import AbakusGroup, Penalty
from lego.utils.test_utils import BaseAPITestCase, BaseTestCase


class PoolActivationTestCase(BaseAPITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml', 'test_companies.yaml'
    ]

    _test_pools_data = [
        {
            'name': 'TESTPOOL1',
            'capacity': 2,
            'activation_date': timezone.now(),
            'permission_groups': [1]
        },
    ]

    def setUp(self):
        self.event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.event.start_time = timezone.now() + timedelta(days=1)
        self.event.merge_time = timezone.now() + timedelta(hours=12)
        self.event.save()

        self.pool_one = self.event.pools.get(name='Abakusmember')
        self.pool_two = self.event.pools.get(name='Webkom')

        self.pool_one.activation_date = timezone.now() - timedelta(days=1)
        self.pool_one.capacity = 1
        self.pool_one.save()

        self.pool_two.activation_date = timezone.now() + timedelta(minutes=30)
        self.pool_two.capacity = 2
        self.pool_two.save()

    def test_users_are_bumped_before_pool_activation(self):
        """" Tests that users are bumped right before pool activation """
        users = get_dummy_users(3)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)

        self.assertEqual(self.pool_two.registrations.count(), 0)
        bump_waiting_users_to_new_pool()
        self.assertEqual(self.pool_two.registrations.count(), 2)

    def test_users_are_bumped_after_pool_activation(self):
        """ Tests that users are bumped right after pool activation. """
        users = get_dummy_users(3)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)

        self.pool_two.activation_date = timezone.now() - timedelta(minutes=30)
        self.pool_two.save()

        bump_waiting_users_to_new_pool()

        self.assertEqual(self.pool_two.registrations.count(), 2)

    def test_too_many_users_waiting_for_bump(self):
        """ Tests that only 2 users are bumped to a new pool with capacity = 2. """
        users = get_dummy_users(4)
        registrations = []

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)
            registrations.append(Registration.objects.get(id=registration.id))

        bump_waiting_users_to_new_pool()

        self.assertEqual(self.pool_two.registrations.count(), 2)
        self.assertIsNone(registrations[3].pool)

    def test_isnt_bumped_without_permission(self):
        """ Tests that a waiting user isnt bumped to a pool it cant access. """
        users = get_dummy_users(2)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)

        bump_waiting_users_to_new_pool()

        self.assertEqual(self.pool_two.registrations.count(), 0)
        self.assertEqual(self.event.waiting_registrations.count(), 1)

    def test_isnt_bumped_with_penalties(self):
        """ Users should not be bumped if they have 3 penalties. """
        self.event.start_time = timezone.now() + timedelta(days=1)
        self.event.merge_time = timezone.now() + timedelta(hours=12)
        self.event.save()

        self.pool_one.activation_date = timezone.now() - timedelta(days=1)
        self.pool_one.save()

        self.pool_two.activation_date = timezone.now() + timedelta(minutes=30)
        self.pool_two.save()

        users = get_dummy_users(2)

        Penalty.objects.create(
            user=users[1],
            reason='test',
            weight=3,
            source_event=self.event,
        )

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)

        bump_waiting_users_to_new_pool()

        self.assertEqual(self.pool_two.registrations.count(), 0)
        self.assertEqual(self.event.waiting_registrations.count(), 1)

    def test_isnt_bumped_if_activation_is_far_into_the_future(self):
        """ Users should not be bumped if the pool is activated more than
            35 minutes in the future. """
        self.pool_two.activation_date = timezone.now() + timedelta(minutes=40)
        self.pool_two.save()

        users = get_dummy_users(2)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)

        bump_waiting_users_to_new_pool()

        self.assertEqual(self.pool_two.registrations.count(), 0)
        self.assertEqual(self.event.waiting_registrations.count(), 1)

    def test_isnt_bumped_if_activation_is_far_into_the_past(self):
        """ Users should not be bumped if the pool is activated more than
            35 minutes in the past. """
        users = get_dummy_users(2)

        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)

        self.pool_two.activation_date = timezone.now() - timedelta(minutes=40)
        self.pool_two.save()
        AbakusGroup.objects.get(name='Webkom').add_user(users[1])

        bump_waiting_users_to_new_pool()

        self.assertEqual(self.pool_two.registrations.count(), 0)
        self.assertEqual(self.event.waiting_registrations.count(), 1)

    def test_ensure_pool_counters_raise_error_when_incorrect(self):
        """Test that counter raises error due to incorrect counter"""

        users = get_dummy_users(3)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            Registration.objects.get_or_create(event=self.event, user=user, pool=self.pool_one)

        self.assertGreater(self.pool_one.registrations.count(), self.pool_one.counter)

        with self.assertRaises(PoolCounterNotEqualToRegistrationCount):
            check_that_pool_counters_match_registration_number()

    def test_ensure_pool_counters_match_registration_number(self):
        """Test that method does not raise error when counter is ok"""

        self.assertEqual(self.pool_one.registrations.count(), self.pool_one.counter)
        check_that_pool_counters_match_registration_number()

    def test_pool_counter_check_ignore_merged_events(self):
        """Test that counter raises error due to incorrect counter"""

        self.event.merge_time = timezone.now() - timedelta(days=1)
        self.event.save()
        users = get_dummy_users(3)

        for user in users:
            AbakusGroup.objects.get(name='Webkom').add_user(user)
            reg = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(reg)

        self.assertGreater(self.pool_one.registrations.count(), self.pool_one.counter)

        check_that_pool_counters_match_registration_number()


class PenaltyExpiredTestCase(BaseTestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml', 'test_companies.yaml'
    ]

    def setUp(self):
        self.event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.event.heed_penalties = True
        self.event.start_time = timezone.now() + timedelta(days=1)
        self.event.merge_time = timezone.now() + timedelta(hours=12)
        self.event.save()
        for pool in self.event.pools.all():
            pool.activation_time = timezone.now() - timedelta(days=1)
            pool.capacity = 1
            pool.save()

    def test_is_automatically_bumped_after_penalty_expiration(self):
        """ Tests that the user that registered with penalties is bumped
            by the task after penalty expiration"""

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        p1 = Penalty.objects.create(user=user, reason='test', weight=3, source_event=self.event)

        registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
        async_register(registration.id)

        make_penalty_expire(p1)
        check_events_for_registrations_with_expired_penalties.delay()

        self.assertIsNotNone(Registration.objects.get(id=registration.id).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    def test_is_bumped_with_multiple_penalties(self):
        """ Tests that a user is bumped when going from 4 to 2 active penalties"""

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        p1 = Penalty.objects.create(user=user, reason='test', weight=2, source_event=self.event)
        Penalty.objects.create(user=user, reason='test2', weight=2, source_event=self.event)

        registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
        async_register(registration.id)

        make_penalty_expire(p1)
        check_events_for_registrations_with_expired_penalties.delay()

        self.assertIsNotNone(Registration.objects.get(id=registration.id).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    def test_isnt_bumped_with_too_many_penalties(self):
        """ Tests that a user isn't bumped when going from 4 to 3 active penalties """

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        p1 = Penalty.objects.create(user=user, reason='test', weight=1, source_event=self.event)
        Penalty.objects.create(user=user, reason='test2', weight=3, source_event=self.event)

        registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
        async_register(registration.id)

        make_penalty_expire(p1)
        check_events_for_registrations_with_expired_penalties.delay()

        self.assertIsNone(Registration.objects.get(id=registration.id).pool)
        self.assertEqual(self.event.number_of_registrations, 0)

    def test_isnt_bumped_when_full(self):
        """ Tests that a user isnt bumped when the event is full when penalties expire. """

        users = get_dummy_users(2)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)

        p1 = Penalty.objects.create(user=users[1], reason='test', weight=3, source_event=self.event)

        for user in users:
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            async_register(registration.id)

        make_penalty_expire(p1)
        check_events_for_registrations_with_expired_penalties.delay()

        self.assertIsNone(Registration.objects.get(user=users[1]).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    def test_isnt_bumped_when_not_first_in_line(self):
        """ Tests that a user isnt bumped when not first in the waiting list.
            In practice, this should never happen, because the only reason someone
            is in front of you in the list is if the event is full, which is tested above.
        """

        users = get_dummy_users(3)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)

        p1 = Penalty.objects.create(user=users[2], reason='test', weight=3, source_event=self.event)

        for user in users:
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            async_register(registration.id)

        make_penalty_expire(p1)
        check_events_for_registrations_with_expired_penalties.delay()

        self.assertIsNone(Registration.objects.get(user=users[1]).pool)
        self.assertIsNone(Registration.objects.get(user=users[2]).pool)
        self.assertEqual(self.event.number_of_registrations, 1)

    def test_async_bump_post_merge(self):
        """ Tests that a waiting user with penalties is bumped to any pool after merge"""
        self.event.merge_time = timezone.now()
        self.event.save()

        users = get_dummy_users(2)
        for user in users:
            AbakusGroup.objects.get(name='Abakus').add_user(user)

        p1 = Penalty.objects.create(user=users[1], reason='test', weight=3, source_event=self.event)

        for user in users:
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            async_register(registration.id)

        make_penalty_expire(p1)
        check_events_for_registrations_with_expired_penalties.delay()

        self.assertIsNotNone(Registration.objects.get(user=users[1]).pool)
        self.assertEqual(self.event.number_of_registrations, 2)


class PaymentDueTestCase(BaseTestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml', 'test_companies.yaml'
    ]

    def setUp(self):
        self.event = Event.objects.get(title='POOLS_AND_PRICED')
        self.event.start_time = timezone.now() + timedelta(days=1)
        self.event.end_time = timezone.now() + timedelta(days=1, hours=2)
        self.event.merge_time = timezone.now() + timedelta(hours=12)
        self.event.payment_due_date = timezone.now() + timedelta(days=2)
        self.event.save()
        self.registration = self.event.registrations.first()

    @mock.patch('lego.apps.events.tasks.handle_event')
    def test_user_notification_when_overdue_payment_and_in_waiting_list(self, mock_handle_event):
        """Tests that payment notification is not added when registration is in waiting list"""

        self.registration.pool = None
        self.registration.save()
        notify_user_when_payment_soon_overdue.delay()
        mock_handle_event.assert_not_called()

    @mock.patch('lego.apps.events.tasks.handle_event')
    def test_user_notification_when_overdue_payment(self, mock_handle_event):
        """Tests that notification is added when registration has not paid"""

        notify_user_when_payment_soon_overdue.delay()
        mock_handle_event.assert_called_once_with(self.registration, 'payment_overdue')

    @mock.patch('lego.apps.events.tasks.handle_event')
    def test_user_notification_when_time_limit_passed(self, mock_handle_event):
        """Test that notification is added a second time when time limit (1 day) has passed"""
        self.registration.last_notified_overdue_payment = timezone.now() - timedelta(days=1)
        self.registration.save()

        notify_user_when_payment_soon_overdue.delay()
        mock_handle_event.assert_called_once_with(self.registration, 'payment_overdue')

    @mock.patch('lego.apps.events.tasks.handle_event')
    def test_no_notification_when_recently_notified(self, mock_handle_event):
        """Test that notification is not added when registration is within time limit"""

        self.registration.last_notified_overdue_payment = timezone.now()
        self.registration.save()

        notify_user_when_payment_soon_overdue.delay()
        mock_handle_event.assert_not_called()

    @mock.patch('lego.apps.events.tasks.handle_event')
    def test_no_notification_when_user_has_paid(self, mock_handle_event):
        """Test that notification is not added when user has paid"""

        self.registration.charge_status = constants.PAYMENT_SUCCESS
        self.registration.save()

        notify_user_when_payment_soon_overdue.delay()
        mock_handle_event.assert_not_called()

    @mock.patch('lego.apps.events.tasks.handle_event')
    def test_no_notification_when_event_is_not_due(self, mock_handle_event):
        """Test that notification is not added when event is not overdue"""

        self.event.payment_due_date = timezone.now() - timedelta(days=3)
        self.event.save()

        notify_user_when_payment_soon_overdue.delay()
        mock_handle_event.assert_not_called()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_when_event_is_past_due_date(self, mock_notification):
        """Test that email is sent when event is past due and user has not paid"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.save()
        notify_event_creator_when_payment_overdue.delay()
        call = mock_notification.mock_calls[0]
        self.assertEqual(call[1], (self.event.created_by, ))
        self.assertEqual(call[2]['event'], self.event)
        self.assertEqual(1, len(call[2]['users']))
        mock_notification.assert_called_once()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_when_past_due_date_and_charge_failed(self, mock_notification):
        """Test that email is sent when event is past due and user has a failed charge"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.save()
        self.registration.charge_id = 'CHARGE_ID'
        self.registration.charge_status = constants.PAYMENT_FAILURE
        notify_event_creator_when_payment_overdue.delay()
        call = mock_notification.mock_calls[0]
        self.assertEqual(call[1], (self.event.created_by, ))
        self.assertEqual(call[2]['event'], self.event)
        self.assertEqual(1, len(call[2]['users']))
        mock_notification.assert_called_once()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_only_shows_those_who_have_not_paid(self, mock_notification):
        """Test creator notify only list those who has not paid for an overdue event"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        registration_two = Registration.objects.get_or_create(event=self.event, user=user)[0]
        self.event.register(registration_two)
        registration_two.set_payment_success()

        notify_event_creator_when_payment_overdue.delay()
        call = mock_notification.mock_calls[0]
        self.assertEqual(call[1], (self.event.created_by, ))
        self.assertEqual(call[2]['event'], self.event)
        self.assertEqual(1, len(call[2]['users']))
        mock_notification.assert_called_once()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_when_event_is_past_due_date_multiple(self, mock_notification):
        """Test that email is sent when event is past due and multiple users has not paid"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        registration_two = Registration.objects.get_or_create(event=self.event, user=user)[0]
        self.event.register(registration_two)

        notify_event_creator_when_payment_overdue.delay()
        call = mock_notification.mock_calls[0]
        self.assertEqual(call[1], (self.event.created_by, ))
        self.assertEqual(call[2]['event'], self.event)
        self.assertEqual(2, len(call[2]['users']))
        mock_notification.assert_called_once()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_is_not_sent_when_everyone_has_paid(self, mock_notification):
        """Test that email is not sent when event is past due and everyone has paid"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.save()
        self.registration.set_payment_success()

        notify_event_creator_when_payment_overdue.delay()
        mock_notification.assert_not_called()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_is_not_sent_when_not_priced(self, mock_notification):
        """Test that email is not sent when event is not priced"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.is_priced = False
        self.event.save()

        notify_event_creator_when_payment_overdue.delay()
        mock_notification.assert_not_called()

    @mock.patch('lego.apps.events.tasks.EventPaymentOverdueCreatorNotification')
    def test_creator_notification_is_not_sent_past_end_time(self, mock_notification):
        """Test that email is not sent when event is past end time"""

        self.event.payment_due_date = timezone.now() - timedelta(days=2)
        self.event.end_time = timezone.now() - timedelta(hours=1)
        self.event.save()

        notify_event_creator_when_payment_overdue.delay()
        mock_notification.assert_not_called()
