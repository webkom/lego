from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from lego.apps.events import constants
from lego.apps.events.models import Event, Registration
from lego.apps.users.models import AbakusGroup, PenaltyGroup
from lego.utils.test_utils import BaseTestCase

from .utils import get_dummy_users


class PenaltyTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))

    def test_get_earliest_registration_time_ignore_penalties(self):
        """Test method calculating the earliest registration time when penalties are ignored"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.heed_penalties = False
        event.save()

        current_time = timezone.now()
        webkom_pool = event.pools.get(name="Webkom")
        webkom_pool.activation_date = current_time
        webkom_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        PenaltyGroup.objects.create(
            user=user, reason="test", weight=1, source_event=event
        )
        penalties = user.number_of_penalties()

        earliest_reg = event.get_earliest_registration_time(
            user, [webkom_pool], penalties
        )
        self.assertEqual(earliest_reg, current_time)

    def test_get_earliest_registration_time_one_or_more_penalty(self):
        """Test method calculating the earliest
        registration time for user with one or more penalties"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        current_time = timezone.now()
        webkom_pool = event.pools.get(name="Webkom")
        webkom_pool.activation_date = current_time
        webkom_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        PenaltyGroup.objects.create(
            user=user, reason="first test penalty", weight=1, source_event=event
        )
        penalties = user.number_of_penalties()

        earliest_reg = event.get_earliest_registration_time(
            user, [webkom_pool], penalties
        )
        self.assertEqual(
            earliest_reg,
            current_time + timedelta(hours=settings.PENALTY_DELAY_DURATION),
        )
        PenaltyGroup.objects.create(
            user=user, reason="second test penalty", weight=2, source_event=event
        )
        penalties = user.number_of_penalties()

        earliest_reg = event.get_earliest_registration_time(
            user, [webkom_pool], penalties
        )
        self.assertEqual(
            earliest_reg,
            current_time + timedelta(hours=settings.PENALTY_DELAY_DURATION),
        )

    def test_cant_register_with_one_or_more_penalty_before_delay(self):
        """Test that user can not register
        before (5 hour) delay when having one or more penalties"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        current_time = timezone.now()
        abakus_pool = event.pools.get(name="Abakusmember")
        abakus_pool.activation_date = current_time
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        PenaltyGroup.objects.create(
            user=user, reason="first test penalty", weight=1, source_event=event
        )
        PenaltyGroup.objects.create(
            user=user, reason="second test penalty", weight=2, source_event=event
        )

        with self.assertRaises(ValueError):
            registration = Registration.objects.get_or_create(event=event, user=user)[0]
            event.register(registration)

    def test_can_register_with_one_or_more_penalty_after_delay(self):
        """Test that user can register after (5 hour)
        delay has passed having one or more penalties"""
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")

        current_time = timezone.now()
        abakus_pool = event.pools.get(name="Abakusmember")
        abakus_pool.activation_date = current_time - timedelta(
            hours=settings.PENALTY_DELAY_DURATION
        )
        abakus_pool.save()

        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Abakus").add_user(user)
        PenaltyGroup.objects.create(
            user=user, reason="first test penalty", weight=1, source_event=event
        )
        PenaltyGroup.objects.create(
            user=user, reason="second test penalty", weight=2, source_event=event
        )

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)
        self.assertEqual(event.number_of_registrations, 1)

    def test_penalties_created_on_unregister(self):
        """Test that user gets penalties on unregister after limit"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        event.unregistration_deadline = timezone.now() - timedelta(days=1)
        event.save()

        registration = event.registrations.first()
        penalties_before = registration.user.number_of_penalties()

        event.unregister(registration)

        penalties_after = registration.user.number_of_penalties()
        self.assertGreater(penalties_after, penalties_before)
        self.assertEqual(penalties_before, 0)
        self.assertEqual(penalties_after, event.penalty_weight)

    def test_penalties_created_when_not_present_and_not_heed_penalties(self):
        """Test that user does not get penalties when not present and event not heeding penalties"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        event.heed_penalties = False
        event.save()

        registration = event.registrations.first()
        penalties_before = registration.user.number_of_penalties()

        registration.set_presence(constants.PRESENCE_CHOICES.NOT_PRESENT)

        penalties_after = registration.user.number_of_penalties()
        self.assertEqual(penalties_before, 0)
        self.assertEqual(penalties_after, 0)

    def test_penalties_created_when_not_present(self):
        """Test that user gets penalties when not present"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")

        registration = event.registrations.first()
        penalties_before = registration.user.number_of_penalties()

        registration.set_presence(constants.PRESENCE_CHOICES.NOT_PRESENT)

        penalties_after = registration.user.number_of_penalties()
        self.assertEqual(penalties_before, 0)
        self.assertEqual(penalties_after, event.penalty_weight_on_not_present)

    def test_penalties_removed_when_not_present_changes(self):
        """Test that penalties for not_present gets removed when resetting presence"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        registration = event.registrations.first()
        registration.set_presence(constants.PRESENCE_CHOICES.NOT_PRESENT)

        penalties_before = registration.user.number_of_penalties()
        registration.set_presence(constants.PRESENCE_CHOICES.UNKNOWN)

        penalties_after = registration.user.number_of_penalties()
        self.assertEqual(penalties_before, event.penalty_weight_on_not_present)
        self.assertEqual(penalties_after, 0)

    def test_only_correct_penalties_are_removed_on_presence_change(self):
        """Test that only penalties for given event are removed when changing presence"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        other_event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        registration = event.registrations.first()

        registration.set_presence(constants.PRESENCE_CHOICES.NOT_PRESENT)
        penalties_before = registration.user.number_of_penalties()
        penalties_object_before = list(registration.user.penalty_groups.all())

        PenaltyGroup.objects.create(
            user=registration.user,
            reason="OTHER EVENT",
            weight=2,
            source_event=other_event,
        )
        penalties_during = registration.user.number_of_penalties()
        penalties_objects_during = list(registration.user.penalty_groups.all())

        registration.set_presence(constants.PRESENCE_CHOICES.UNKNOWN)
        penalties_after = registration.user.number_of_penalties()
        penalties_object_after = list(registration.user.penalty_groups.all())

        self.assertEqual(penalties_object_before[0].source_event, event)
        self.assertEqual(penalties_object_after[0].source_event, other_event)
        self.assertEqual(len(penalties_object_before), 1)
        self.assertEqual(len(penalties_objects_during), 2)
        self.assertEqual(len(penalties_object_after), 1)
        self.assertEqual(penalties_before, event.penalty_weight_on_not_present)
        self.assertEqual(
            penalties_during,
            event.penalty_weight_on_not_present
            + other_event.penalty_weight_on_not_present,
        )
        self.assertEqual(penalties_after, other_event.penalty_weight_on_not_present)

    def test_able_to_register_when_not_heed_penalties_with_penalties(self):
        """Test that user is able to register when heed_penalties is false and user has penalties"""
        event = Event.objects.get(title="POOLS_WITH_REGISTRATIONS")
        other_event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        event.heed_penalties = False
        event.save()
        user = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(user)
        PenaltyGroup.objects.create(
            user=user, reason="TEST", weight=3, source_event=other_event
        )

        registration = Registration.objects.get_or_create(event=event, user=user)[0]
        event.register(registration)

        registration.refresh_from_db()
        self.assertIsNotNone(registration.pool)
