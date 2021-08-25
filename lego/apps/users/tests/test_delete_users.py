from datetime import timedelta

from django.utils import timezone

from lego.apps.events.models import Event, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase


class DeleteUserTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            merge_time=timezone.now() + timedelta(hours=12),
        )

    def test_delete_user_registration_before_start_time(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event_id = event.id
        users = get_dummy_users(4)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        registration = event.registrations.exclude(pool=None).first()
        user_id = registration.user.id
        no_of_regs_before = event.number_of_registrations
        no_of_waiting_registrations_before = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_before, 1)

        User.objects.get(id=user_id).delete(force=True)
        event.refresh_from_db()
        no_of_waiting_registrations_after = event.waiting_registrations.count()

        # Check that users have been bumped
        self.assertEqual(no_of_waiting_registrations_after, 0)
        self.assertEqual(event.number_of_registrations, no_of_regs_before)
        # Verify that the event still exists
        self.assertEqual(len(Event.objects.all().filter(id=event_id)), 1)
        # Verify that user is deleted
        self.assertEqual(len(User.objects.all().filter(id=user_id)), 0)
        # Legacy_registration_count should not be incremented if the event has not started
        self.assertEqual(event.legacy_registration_count, 0)

    def test_delete_user_registration_after_start_time(self):
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event_id = event.id
        users = get_dummy_users(4)

        for user in users:
            AbakusGroup.objects.get(name="Abakus").add_user(user)
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

        event.start_time = timezone.now() - timedelta(hours=3)
        event.save()

        self.assertLess(event.unregistration_close_time, timezone.now())
        registration = event.registrations.exclude(pool=None).first()
        user_id = registration.user.id
        no_of_regs_before = event.number_of_registrations
        no_of_waiting_registrations_before = event.waiting_registrations.count()
        self.assertEqual(no_of_waiting_registrations_before, 1)

        User.objects.get(id=user_id).delete(force=True)
        event.refresh_from_db()
        no_of_waiting_registrations_after = event.waiting_registrations.count()

        # Check that users have not been bumped
        self.assertEqual(
            no_of_waiting_registrations_after, no_of_waiting_registrations_before
        )
        # Check that users have not been bumped
        self.assertEqual(event.number_of_registrations, no_of_regs_before)
        # Verify that the event still exists
        self.assertEqual(len(Event.objects.all().filter(id=event_id)), 1)
        # Verify that user is deleted
        self.assertEqual(len(User.objects.all().filter(id=user_id)), 0)
        # Legacy_registration_count should be incremented if the event has started
        self.assertEqual(event.legacy_registration_count, 1)
