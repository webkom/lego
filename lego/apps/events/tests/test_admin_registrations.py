from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from lego.apps.events.models import Event, Registration
from lego.apps.users.models import AbakusGroup

from .utils import get_dummy_users


class AdminRegistrationTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_events.yaml']

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12)
        )

    def tearDown(self):
        from django_redis import get_redis_connection
        get_redis_connection('default').flushall()

    def test_admin_registration(self):
        """Test that admin can force register user into chosen pool"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.first()

        no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, no_of_regs_before + 1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before + 1)

    def test_ar_with_wrong_pool(self):
        """Test that admin can not register user into event using pool from other event"""
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
        """Test that admin can register user into pool without user having permission"""
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
        """Test that admin can force register user into pool after merge"""
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
        """Test that admin can force register user into an already full pool"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        users = get_dummy_users(5)
        user = users[4]
        for u in users[:4]:
            AbakusGroup.objects.get(name='Abakus').add_user(u)
            registration = Registration.objects.get_or_create(event=event, user=u)[0]
            event.register(registration)
        pool = event.pools.first()

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before+1)

    def test_ar_to_full_event(self):
        """Test that admin can force register user into an already full event"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        users = get_dummy_users(7)
        user = users[6]
        for u in users[:6]:
            AbakusGroup.objects.get(name='Webkom').add_user(u)
            registration = Registration.objects.get_or_create(event=event, user=u)[0]
            event.register(registration)
        pool = event.pools.first()

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before+1)

    def test_ar_twice(self):
        """Test that user is not registered twice when admin registered is run twice"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        e1_no_of_regs_before = event.number_of_registrations

        event.admin_register(user, pool)
        event.admin_register(user, pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before+1)
