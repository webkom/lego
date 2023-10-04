from unittest import mock

from django.test import override_settings
from django.utils import timezone
from django.utils.timezone import timedelta

from lego import settings
from lego.apps.events.models import Event, Pool
from lego.apps.files.models import File
from lego.apps.users import constants
from lego.apps.users.constants import (
    PHOTO_CONSENT_DOMAINS,
    SOCIAL_MEDIA_DOMAIN,
    WEBSITE_DOMAIN,
)
from lego.apps.users.models import (
    AbakusGroup,
    Membership,
    Penalty,
    PenaltyGroup,
    PhotoConsent,
    User,
)
from lego.apps.users.registrations import Registrations
from lego.apps.users.tasks import expire_penalties_if_six_events_has_passed
from lego.utils.test_utils import BaseAPITestCase, BaseTestCase, fake_time


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
        union = set(
            list(abakus.get_descendants(include_self=True))
            + list(users.get_descendants(include_self=True))
            + list(students.get_descendants(include_self=True))
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
        self.assertEqual(self.user.past_memberships.count(), 1)

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
        self.assertEqual(self.user.past_memberships.count(), 1)

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


class AsyncTestCase(BaseAPITestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.test_user = User.objects.get(pk=1)
        self.source = Event.objects.all().first()

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 10))
    def test_async_expire_penalties_if_six_events_has_passed(self, mock_now):
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=8),
            user=self.test_user,
            reason="first_penalty",
            weight=1,
            source_event=self.source,
        )

        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=5),
            user=self.test_user,
            reason="second_penalty",
            weight=2,
            source_event=self.source,
        )
        self.assertEqual(self.test_user.number_of_penalties(), 3)

        webkom_group = AbakusGroup.objects.get(name="Webkom")
        webkom_group.add_user(self.test_user)
        webkom_group.save()
        self.test_user.save()

        for _i in range(6):
            event = Event.objects.create(
                title="AbakomEvent",
                event_type=0,
                start_time=mock_now(),
                end_time=mock_now(),
            )
            pool = Pool.objects.create(
                name="Pool1",
                event=event,
                capacity=0,
                activation_date=timezone.now() - timedelta(days=1),
            )

            pool.permission_groups.set([webkom_group])

        expire_penalties_if_six_events_has_passed()

        self.assertEqual(self.test_user.number_of_penalties(), 2)


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

    def test_natural_key(self):
        found_membership = Membership.objects.get_by_natural_key(
            self.test_user.username, self.test_committee.name
        )
        self.assertEqual(self.test_membership, found_membership)


class PenaltyTestCase(BaseTestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.test_user = User.objects.get(pk=1)
        self.source = Event.objects.all().first()

    def test_create_penalty_group(self):
        penalty_group = PenaltyGroup.objects.create(
            user=self.test_user, reason="test", source_event=self.source, weight=1
        )

        penalties = Penalty.objects.filter(penalty_group__user=self.test_user)

        self.assertEqual(len(penalties), 1)

        self.assertEqual(self.test_user.number_of_penalties(), 1)
        self.assertEqual(self.test_user, penalty_group.user)
        self.assertEqual("test", penalty_group.reason)
        self.assertEqual(1, penalty_group.weight)
        self.assertEqual(self.source, penalty_group.source_event)
        self.assertEqual(self.source.id, penalty_group.source_event.id)

    def test_count_weights(self):
        weights = [1, 2]
        for weight in weights:
            PenaltyGroup.objects.create(
                user=self.test_user,
                reason="test",
                source_event=self.source,
                weight=weight,
            )

        self.assertEqual(self.test_user.number_of_penalties(), sum(weights))

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 10))
    def test_only_count_active_penalties(self, mock_now):
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=11),
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=self.source,
        )

        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=9),
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=self.source,
        )
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=5),
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=self.source,
        )
        PenaltyGroup.objects.create(
            created_at=mock_now(),
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=self.source,
        )

        self.assertEqual(self.test_user.number_of_penalties(), 3)

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 10))
    def test_penalty_group_activation_period(self, mock_now):
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=8),
            user=self.test_user,
            reason="first_penalty",
            weight=1,
            source_event=self.source,
        )

        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=2),
            user=self.test_user,
            reason="second_penalty",
            weight=2,
            source_event=self.source,
        )

        self.assertEqual(
            (
                PenaltyGroup.objects.get(reason="first_penalty").activation_time.day,
                PenaltyGroup.objects.get(reason="first_penalty").exact_expiration.day,
            ),
            (2, 12),
        )
        self.assertEqual(
            (
                PenaltyGroup.objects.get(reason="second_penalty").activation_time.day,
                PenaltyGroup.objects.get(reason="second_penalty").exact_expiration.day,
            ),
            (12, 1),
        )

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 10))
    def test_penalty_expiration_after_6_events_on_penalty_with_weight_one(
        self, mock_now
    ):
        """Tests that The first active penalty is
        expired and the rest are adjusted after 6 events"""

        self.test_user.check_for_expirable_penalty()

        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=8),
            user=self.test_user,
            reason="first_penalty",
            weight=1,
            source_event=self.source,
        )

        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=5),
            user=self.test_user,
            reason="second_penalty",
            weight=2,
            source_event=self.source,
        )

        # The timeline currently is: 1: 2-12, 2: 12-22, 3: 22-1
        self.assertEqual(self.test_user.number_of_penalties(), 3)

        webkom_group = AbakusGroup.objects.get(name="Webkom")
        webkom_group.add_user(self.test_user)
        webkom_group.save()
        self.test_user.save()

        for _i in range(6):
            event = Event.objects.create(
                title="AbakomEvent",
                event_type=0,
                start_time=mock_now(),
                end_time=mock_now(),
            )
            pool = Pool.objects.create(
                name="Pool1",
                event=event,
                capacity=0,
                activation_date=timezone.now() - timedelta(days=1),
            )

            pool.permission_groups.set([webkom_group])

        self.test_user.check_for_expirable_penalty()
        # Tests that the changes happened after 6 events
        # The timeline now should be is: 1: 10-20, 2: 20-30
        self.assertEqual(self.test_user.number_of_penalties(), 2)
        self.assertEqual(
            (
                Penalty.objects.valid()[0].activation_time.day,
                Penalty.objects.valid()[0].exact_expiration.day,
                Penalty.objects.valid()[1].exact_expiration.day,
            ),
            (10, 20, 30),
        )

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 10, 10))
    def test_penalty_expiration_after_6_events_on_penalty_with_weight_two(
        self, mock_now
    ):
        """Tests that The weight of the first active penalty
        is decremented and the rest are adjusted after 6 events"""
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=8),
            user=self.test_user,
            reason="first_penalty",
            weight=2,
            source_event=self.source,
        )

        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=5),
            user=self.test_user,
            reason="second_penalty",
            weight=1,
            source_event=self.source,
        )

        webkom_group = AbakusGroup.objects.get(name="Webkom")
        webkom_group.add_user(self.test_user)
        webkom_group.save()
        self.test_user.save()

        for _i in range(5):
            event = Event.objects.create(
                title="AbakomEvent",
                event_type=0,
                start_time=mock_now() - timedelta(days=6),
                end_time=mock_now() - timedelta(days=6),
            )
            pool = Pool.objects.create(
                name="Pool1",
                event=event,
                capacity=0,
                activation_date=timezone.now() - timedelta(days=1),
            )

            pool.permission_groups.set([webkom_group])

        self.test_user.check_for_expirable_penalty()

        # Tests first that nothing is changed after 5 events
        self.assertEqual(self.test_user.number_of_penalties(), 3)
        self.assertEqual(
            (
                Penalty.objects.valid()[0].exact_expiration.day,
                Penalty.objects.valid()[1].exact_expiration.day,
                Penalty.objects.valid()[2].exact_expiration.day,
            ),
            (12, 22, 1),
        )

        event = Event.objects.create(
            title="AbakomEvent",
            event_type=0,
            start_time=mock_now() - timedelta(days=6),
            end_time=mock_now() - timedelta(days=6),
        )
        pool = Pool.objects.create(
            name="Pool1",
            event=event,
            capacity=0,
            activation_date=timezone.now() - timedelta(days=1),
        )
        self.test_user.check_for_expirable_penalty()
        # Tests that the new event is not counted if
        # the users does not have permission to the pool
        self.assertEqual(self.test_user.number_of_penalties(), 3)

        pool.permission_groups.set([webkom_group])

        self.test_user.check_for_expirable_penalty()

        # Tests that the changes happened after 6 events
        self.assertEqual(self.test_user.number_of_penalties(), 2)
        self.assertEqual(
            (
                Penalty.objects.valid()[0].exact_expiration.day,
                Penalty.objects.valid()[1].exact_expiration.day,
            ),
            (20, 30),
        )

    @override_settings(PENALTY_IGNORE_WINTER=((12, 10), (1, 10)))
    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 12, 20))
    def test_frozen_penalties_count_as_active_winter(self, mock_now):
        penalty1 = PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=19, hours=23, minutes=59),
            user=self.test_user,
            reason="penalty1",
            weight=1,
            source_event=self.source,
        )

        penalty2 = PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=20),
            user=self.test_user,
            reason="penalty2",
            weight=1,
            source_event=self.source,
        )

        self.assertEqual(self.test_user.number_of_penalties(), 2)
        self.assertEqual(
            (penalty1.activation_time.day, penalty1.activation_time.month),
            (30, 11),
        )
        self.assertEqual(
            (penalty2.activation_time.day, penalty2.activation_time.month),
            (11, 1),
        )

    @override_settings(PENALTY_IGNORE_SUMMER=((6, 12), (8, 15)))
    @mock.patch("django.utils.timezone.now", return_value=fake_time(2016, 6, 22))
    def test_frozen_penalties_count_as_active_summer(self, mock_now):
        # This penalty is created slightly less than 10 days from the freeze-point.
        # It should be counted as active.
        penalty1 = PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=19, hours=23, minutes=59),
            user=self.test_user,
            reason="active",
            weight=1,
            source_event=self.source,
        )

        # This penalty is created exactly 10 days from the freeze-point.
        # It should be counted as inactive.
        penalty2 = PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=20),
            user=self.test_user,
            reason="inactive",
            weight=1,
            source_event=self.source,
        )

        self.assertEqual(self.test_user.number_of_penalties(), 2)
        self.assertEqual(
            (penalty1.activation_time.day, penalty1.activation_time.month),
            (2, 6),
        )
        self.assertEqual(
            (penalty2.activation_time.day, penalty2.activation_time.month),
            (16, 8),
        )

    @override_settings(PENALTY_IGNORE_WINTER=((12, 22), (1, 10)))
    @mock.patch("django.utils.timezone.now", return_value=fake_time(2019, 12, 23))
    def test_penalty_offset_is_calculated_correctly(self, mock_now):
        # This penalty is set to expire the day before the penalty freeze
        # It should not be active
        inactive = PenaltyGroup.objects.create(
            created_at=mock_now().replace(day=10),
            user=self.test_user,
            reason="inactive",
            weight=1,
            source_event=self.source,
        )
        self.assertEqual(self.test_user.number_of_penalties(), 0)
        self.assertEqual(
            (inactive.exact_expiration.month, inactive.exact_expiration.day),
            (12, inactive.created_at.day + settings.PENALTY_DURATION.days),
        )

        active = PenaltyGroup.objects.create(
            created_at=mock_now().replace(day=15),
            user=self.test_user,
            reason="active",
            weight=1,
            source_event=self.source,
        )
        self.assertEqual(
            (active.exact_expiration.month, active.exact_expiration.day),
            (1, 19),
        )

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2019, 10, 10))
    def test_penalty_group_valid_with_one_weight(self, mock_now):
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=10),
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=self.source,
        )
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=9, hours=59, seconds=59),
            user=self.test_user,
            reason="test",
            weight=1,
            source_event=self.source,
        )

        self.assertEqual(len(PenaltyGroup.objects.valid()), 1)

    @mock.patch("django.utils.timezone.now", return_value=fake_time(2019, 10, 10))
    def test_penalty_group_valid_with_two_weight(self, mock_now):
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=20),
            user=self.test_user,
            reason="test",
            weight=2,
            source_event=self.source,
        )
        PenaltyGroup.objects.create(
            created_at=mock_now() - timedelta(days=15),
            user=self.test_user,
            reason="test",
            weight=2,
            source_event=self.source,
        )
        self.assertEqual(len(PenaltyGroup.objects.valid()), 1)


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
