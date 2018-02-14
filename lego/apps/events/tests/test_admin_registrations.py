from datetime import timedelta

from django.utils import timezone

from lego.apps.events.exceptions import RegistrationExists
from lego.apps.events.models import Event, Registration
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase

from .utils import get_dummy_users


class AdminRegistrationTestCase(BaseTestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml', 'test_events.yaml'
    ]

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12)
        )

    def test_admin_registration(self):
        """Test that admin can force register user into chosen pool"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.first()

        no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, admin_registration_reason='test', pool=pool)
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
            event_one.admin_register(user, admin_registration_reason='test', pool=wrong_pool)
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

        event.admin_register(user, admin_registration_reason='test', pool=pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before + 1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before + 1)

    def test_ar_after_merge(self):
        """Test that admin can force register user into pool after merge"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.merge_time = timezone.now() - timedelta(hours=12)
        user = get_dummy_users(1)[0]
        pool = event.pools.first()

        e1_no_of_regs_before = event.number_of_registrations
        pool_no_of_regs_before = pool.registrations.count()

        event.admin_register(user, admin_registration_reason='test', pool=pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before + 1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before + 1)

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

        event.admin_register(user, admin_registration_reason='test', pool=pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before + 1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before + 1)

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

        event.admin_register(user, admin_registration_reason='test', pool=pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before + 1)
        self.assertEqual(pool.registrations.count(), pool_no_of_regs_before + 1)

    def test_ar_twice(self):
        """Test that user is not registered twice when admin registered is run twice"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        pool = event.pools.get(name='Webkom')
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        e1_no_of_regs_before = event.number_of_registrations

        event.admin_register(user, admin_registration_reason='test', pool=pool)
        with self.assertRaises(RegistrationExists):
            event.admin_register(user, admin_registration_reason='test', pool=pool)
        self.assertEqual(event.number_of_registrations, e1_no_of_regs_before + 1)

    def test_ar_without_pool(self):
        """Test that admin registration without pool puts the registration in the waiting list"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name='Abakus').add_user(user)

        waiting_regs_before = event.waiting_registrations.count()

        event.admin_register(user, admin_registration_reason='test')
        self.assertEqual(event.waiting_registrations.count(), waiting_regs_before + 1)

    def test_admin_unreg(self):
        """Test that admin unregistration from waiting list"""
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        event.created_by = User.objects.all().first()
        event.save()
        reg = event.registrations.exclude(pool=None).first()

        regs_before = event.number_of_registrations

        event.admin_unregister(reg.user, admin_unregistration_reason='test')
        self.assertEqual(event.number_of_registrations, regs_before - 1)

    def test_admin_unreg_does_not_give_penalties(self):
        """Test that admin unregistration does not automatically give penalties"""
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        event.created_by = User.objects.all().first()
        event.unregistration_deadline = timezone.now() - timedelta(days=1)
        event.heed_penalties = True
        event.save()
        reg = event.registrations.exclude(pool=None).first()

        regs_before = event.number_of_registrations

        event.admin_unregister(reg.user, admin_unregistration_reason='test')
        self.assertEqual(event.number_of_registrations, regs_before - 1)
        self.assertEqual(reg.user.number_of_penalties(), 0)

    def test_admin_unreg_from_waiting_list(self):
        """Test that admin unregistration from waiting list"""
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        event.created_by = User.objects.all().first()
        event.save()
        reg = event.registrations.first()
        reg.pool = None
        reg.save()

        waiting_regs_before = event.waiting_registrations.count()

        event.admin_unregister(reg.user, admin_unregistration_reason='test')
        self.assertEqual(event.waiting_registrations.count(), waiting_regs_before - 1)
