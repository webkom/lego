from unittest import mock

from django.db import transaction
from django.test import override_settings
from django.utils import timezone
from django.utils.timezone import timedelta

from lego.apps.events.models import Event
from lego.apps.files.models import File
from lego.apps.users import constants
from lego.apps.users.constants import (
    PHOTO_CONSENT_DOMAINS,
    SOCIAL_MEDIA_DOMAIN,
    WEBSITE_DOMAIN,
)
from lego.apps.users.models import AbakusGroup, Membership, Penalty, PhotoConsent, User
from lego.apps.users.registrations import Registrations
from lego.utils.test_utils import BaseTestCase, fake_time


class AbakusGroupTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.non_committee = AbakusGroup(name="testgroup")
        self.non_committee.save()

    def test_natural_key(self):
        found_group = AbakusGroup.objects.get_by_natural_key(self.non_committee.name)
        self.assertEqual(self.non_committee, found_group)


class AbakusGroupHierarchyTestCase(BaseTestCase):
    fixtures = ["initial_files.yaml", "initial_abakus_groups.yaml"]

    def setUp(self):
        self.abakom = AbakusGroup.objects.get(name="Abakom")

    def test_find_all_children(self):
        committees = AbakusGroup.objects.filter(parent=self.abakom.pk)
        children = self.abakom.get_children()
        self.assertEqual(len(committees), len(children))

    def test_abakom_is_root(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        self.assertTrue(abakus.is_root_node())

    def test_get_ancestors(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        webkom = AbakusGroup.objects.get(name="Webkom")

        ancestors = set(webkom.get_ancestors())

        self.assertEqual(len(ancestors), 2)
        self.assertTrue(abakus in ancestors)
        self.assertTrue(self.abakom in ancestors)

    def test_get_ancestors_include_self(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        webkom = AbakusGroup.objects.get(name="Webkom")

        ancestors = set(webkom.get_ancestors(include_self=True))

        self.assertEqual(len(ancestors), 3)
        self.assertTrue(webkom in ancestors)
        self.assertTrue(abakus in ancestors)
        self.assertTrue(self.abakom in ancestors)

    def test_get_descendants(self):
        webkom = AbakusGroup.objects.get(name="Webkom")
        first = AbakusGroup.objects.create(name="first", parent=webkom)
        second = AbakusGroup.objects.create(name="second", parent=first)

        descendants = webkom.get_descendants()
        self.assertEqual(len(descendants), 2)
        self.assertTrue(first in descendants)
        self.assertTrue(second in descendants)

    def test_get_descendants_include_self(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        users = AbakusGroup.objects.get(name="Users")
        students = AbakusGroup.objects.get(name="Students")
        ordained = AbakusGroup.objects.get(name="Ordenen")
        fund = AbakusGroup.objects.get(name="Fondsstyret")
        union = set(
            list(abakus.get_descendants(include_self=True))
            + list(users.get_descendants(include_self=True))
            + list(students.get_descendants(include_self=True))
            + list(ordained.get_descendants(include_self=True))
            + list(fund.get_descendants(include_self=True))
        )
        self.assertEqual(set(AbakusGroup.objects.all()), union)


class UserTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_files.yaml"]

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_full_name(self):
        full_name = "{0} {1}".format(self.user.first_name, self.user.last_name)
        self.assertEqual(full_name, self.user.get_full_name())

    def test_short_name(self):
        self.assertEqual(self.user.get_short_name(), self.user.first_name)

    def test_default_avatar(self):
        self.assertEqual(self.user.profile_picture, "default_male_avatar.png")
        self.user.gender = constants.FEMALE
        self.user.save()
        self.assertEqual(self.user.profile_picture, "default_female_avatar.png")

    def test_set_profile_picture(self):
        self.assertEqual(self.user.profile_picture, "default_male_avatar.png")
        self.user.profile_picture = File.objects.get(key="abakus.png")
        self.user.save()
        self.assertEqual(self.user.profile_picture, "abakus.png")
        self.user.gender = constants.FEMALE
        self.user.save()
        self.assertEqual(self.user.profile_picture, "abakus.png")

    def test_all_groups(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        abakom = AbakusGroup.objects.get(name="Abakom")
        webkom = AbakusGroup.objects.get(name="Webkom")

        webkom.add_user(self.user)
        abakus_groups = self.user.all_groups

        self.assertEqual(len(abakus_groups), 3)
        self.assertTrue(webkom in abakus_groups)
        self.assertTrue(abakom in abakus_groups)
        self.assertTrue(abakus in abakus_groups)

    def test_number_of_users(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        abakom = AbakusGroup.objects.get(name="Abakom")
        webkom = AbakusGroup.objects.get(name="Webkom")

        abakus.add_user(self.user)
        abakom.add_user(User.objects.get(pk=2))
        webkom.add_user(User.objects.get(pk=3))

        self.assertEqual(abakus.number_of_users, 3)
        self.assertEqual(abakom.number_of_users, 2)
        self.assertEqual(webkom.number_of_users, 1)

    def test_add_remove_user(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        self.assertEqual(self.user.memberships.count(), 0)
        self.assertEqual(self.user.past_memberships.count(), 0)

        abakus.add_user(self.user)
        self.assertEqual(abakus.number_of_users, 1)
        self.assertEqual(self.user.memberships.count(), 1)

        abakus = AbakusGroup.objects.get(name="Abakus")
        abakus.remove_user(self.user)
        self.assertEqual(abakus.number_of_users, 0)
        self.assertEqual(self.user.memberships.count(), 0)
        transaction.on_commit(
            lambda: self.assertEqual(self.user.past_memberships.count(), 1)
        )

    def test_add_user_delete_group(self):
        abakus = AbakusGroup.objects.get(name="Abakus")
        self.assertEqual(self.user.memberships.count(), 0)
        self.assertEqual(self.user.past_memberships.count(), 0)

        abakus.add_user(self.user)
        self.assertEqual(abakus.number_of_users, 1)
        self.assertEqual(self.user.memberships.count(), 1)

        abakus = AbakusGroup.objects.get(name="Abakus")
        abakus.remove_user(self.user)
        self.assertEqual(self.user.memberships.count(), 0)
        transaction.on_commit(
            lambda: self.assertEqual(self.user.past_memberships.count(), 1)
        )

        abakus.add_user(self.user)
        self.assertEqual(self.user.memberships.count(), 1)
        self.assertEqual(self.user.past_memberships.count(), 1)

        abakus.delete()
        self.assertEqual(self.user.memberships.count(), 0)
        self.assertEqual(self.user.past_memberships.count(), 0)

    def test_add_user_to_two_groups(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        self.assertEqual(AbakusGroup.objects.get(name="Abakus").number_of_users, 1)
        self.assertEqual(AbakusGroup.objects.get(name="Webkom").number_of_users, 0)

        AbakusGroup.objects.get(name="Webkom").add_user(self.user)
        self.assertEqual(AbakusGroup.objects.get(name="Abakus").number_of_users, 1)
        self.assertEqual(AbakusGroup.objects.get(name="Webkom").number_of_users, 1)

    def test_natural_key(self):
        found_user = User.objects.get_by_natural_key(self.user.username)
        self.assertEqual(self.user, found_user)

    def test_validate_registration_token(self):
        registration_token = Registrations.generate_registration_token("test1@user.com")
        token_email = Registrations.validate_registration_token(registration_token)
        self.assertEqual(token_email, "test1@user.com")

        registration_token = Registrations.generate_registration_token("test1@user.com")
        token_email = Registrations.validate_registration_token(registration_token)
        self.assertNotEqual(token_email, "wrongtest1@user.com")


class MembershipTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.test_committee = AbakusGroup.objects.get(name="Webkom")
        self.test_user = User.objects.get(pk=1)
        self.test_membership = Membership(
            user=self.test_user,
            abakus_group=self.test_committee,
            role=constants.TREASURER,
        )
        self.test_membership.save()

    def test_to_string(self):
        self.assertEqual(
            str(self.test_membership),
            "{0} is {1} in {2}".format(
                self.test_membership.user,
                self.test_membership.get_role_display(),
                self.test_membership.abakus_group,
            ),
        )


class PenaltyTestCase(BaseTestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.test_user = User.objects.get(pk=1)

    def test_create_penalty(self):
        source = Event.objects.all().first()
        penalty = Penalty.objects.create(
            user=self.test_user, reason="test", weight=1, source_event=source
        )

        self.assertEqual(self.test_user.number_of_penalties(), 1)
        self.assertEqual(self.test_user, penalty.user)
        self.assertEqual("test", penalty.reason)
        self.assertEqual(1, penalty.weight)
        self.assertEqual(source, penalty.source_event)
        self.assertEqual(source.id, penalty.source_event.id)

    def test_count_weights(self):
        source = Event.objects.all().first()
        weights = [1, 2]
        for weight in weights:
            Penalty.objects.create(
                user=self.test_user,
                reason="test",
                weight=weight,
                source_event=source,
            )

        self.assertEqual(self.test_user.number_of_penalties(), sum(weights))

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 1))
    def test_only_count_active_penalties(self, mock_now):
        event1 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now() - timedelta(days=20),
            end_time=mock_now() - timedelta(days=20),
        )

        event2 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now() - timedelta(days=19, hours=23, minutes=59),
            end_time=mock_now() - timedelta(days=19, hours=23, minutes=59),
        )

        Penalty.objects.create(
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=event1,
        )
        Penalty.objects.create(
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=event2,
        )
        self.assertEqual(self.test_user.number_of_penalties(), 1)

    @override_settings(PENALTY_IGNORE_WINTER=((12, 10), (1, 10)))
    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 12, 10))
    def test_frozen_penalties_count_as_active_winter(self, mock_now):
        # This event is created slightly less than 20 days from the freeze-point.
        # The penalty should be counted as active.
        event1 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now().replace(day=1),
            end_time=mock_now().replace(day=1),
        )

        Penalty.objects.create(
            created_at=mock_now() - timedelta(days=20, hours=23, minutes=59),
            user=self.test_user,
            reason="active",
            weight=1,
            source_event=event1,
        )

        # This event is created exactly 20 days from the freeze-point.
        # The penalty should be counted as inactive.
        event2 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now() - timedelta(days=21),
            end_time=mock_now() - timedelta(days=21),
        )
        Penalty.objects.create(
            user=self.test_user,
            reason="inactive",
            weight=1,
            source_event=event2,
        )

        self.assertEqual(self.test_user.number_of_penalties(), 1)
        self.assertEqual(self.test_user.penalties.valid().first().reason, "active")

    @override_settings(PENALTY_IGNORE_SUMMER=((6, 12), (8, 15)))
    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 6, 12))
    def test_frozen_penalties_count_as_active_summer(self, mock_now):
        # This event is created slightly less than 20 days from the freeze-point.
        # The penalty should be counted as active.
        event1 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now() - timedelta(days=19, hours=23, minutes=59),
            end_time=mock_now() - timedelta(days=19, hours=23, minutes=59),
        )

        Penalty.objects.create(
            user=self.test_user,
            reason="active",
            weight=1,
            source_event=event1,
        )

        # This event is created exactly 20 days from the freeze-point.
        # The penalty should be counted as inactive.
        event2 = Event.objects.create(
            title="Another simple event",
            event_type=0,
            start_time=mock_now() - timedelta(days=21),
            end_time=mock_now() - timedelta(days=21),
        )
        Penalty.objects.create(
            user=self.test_user,
            reason="inactive",
            weight=1,
            source_event=event2,
        )

        self.assertEqual(self.test_user.number_of_penalties(), 1)
        self.assertEqual(self.test_user.penalties.valid().first().reason, "active")

    @override_settings(PENALTY_IGNORE_WINTER=((12, 22), (1, 10)))
    @mock.patch("django.utils.timezone.now", return_value=fake_time(2019, 12, 23))
    def test_penalty_offset_is_calculated_correctly(self, mock_now):
        # This penalty is set to expire the day before the penalty freeze
        # It should not be active
        event1 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now().replace(day=1),
            end_time=mock_now().replace(day=1),
        )

        inactive = Penalty.objects.create(
            user=self.test_user,
            reason="inactive",
            weight=1,
            source_event=event1,
        )
        self.assertEqual(self.test_user.number_of_penalties(), 0)
        self.assertEqual(
            (inactive.exact_expiration.month, inactive.exact_expiration.day), (12, 21)
        )

        # This penalty is set to expire the same day as the freeze
        event2 = Event.objects.create(
            title="A simple event",
            event_type=0,
            start_time=mock_now().replace(day=2),
            end_time=mock_now().replace(day=2),
        )
        active = Penalty.objects.create(
            user=self.test_user,
            reason="active",
            weight=1,
            source_event=event2,
        )
        self.assertEqual(self.test_user.number_of_penalties(), 1)
        self.assertEqual(
            (active.exact_expiration.month, active.exact_expiration.day), (1, 11)
        )


class PhotoConsentTestCase(BaseTestCase):
    fixtures = [
        "test_users.yaml",
    ]

    def setUp(self):
        self.current_semester = (
            constants.AUTUMN if timezone.now().month > 7 else constants.SPRING
        )
        self.current_year = timezone.now().year
        self.test_user = User.objects.get(pk=1)

    def test_get_consents_without_prior_consents(self):
        initial_consents = self.test_user.photo_consents.all()
        self.assertEqual(len(initial_consents), 0)
        user_consents = PhotoConsent.get_consents(self.test_user)
        self.assertEqual(len(user_consents), 2)
        for consent in user_consents:
            self.assertEqual(consent.semester, self.current_semester)
            self.assertEqual(consent.year, self.current_year)
            self.assertEqual(consent.is_consenting, None)
        self.assertEqual(user_consents[0].domain, SOCIAL_MEDIA_DOMAIN)
        self.assertEqual(user_consents[1].domain, WEBSITE_DOMAIN)

    def test_get_consents_with_prior_consents(self):
        PhotoConsent.objects.create(
            user=self.test_user,
            year=self.current_year,
            semester=self.current_semester,
            domain=WEBSITE_DOMAIN,
            is_consenting=None,
        )
        PhotoConsent.objects.create(
            user=self.test_user,
            year=self.current_year,
            semester=self.current_semester,
            domain=SOCIAL_MEDIA_DOMAIN,
            is_consenting=None,
        )
        initial_consents = self.test_user.photo_consents.all()
        self.assertEqual(len(initial_consents), 2)
        user_consents = PhotoConsent.get_consents(self.test_user)
        self.assertEqual(len(user_consents), 2)

    def test_get_consents_for_past(self):
        """
        It should not be possible to generate new consents for the past.
        """
        user_consents = PhotoConsent.get_consents(self.test_user)
        self.assertEqual(len(user_consents), 2)

        today = timezone.now()

        consents = PhotoConsent.get_consents(
            self.test_user, time=today - timedelta(weeks=52)
        )
        self.assertEqual(len(consents), 0)
        self.assertEqual(
            len(PhotoConsent.get_consents(self.test_user)), len(PHOTO_CONSENT_DOMAINS)
        )
