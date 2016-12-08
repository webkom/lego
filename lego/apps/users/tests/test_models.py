from datetime import timedelta
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from lego.apps.events.models import Event
from lego.apps.social_groups.models import InterestGroup
from lego.apps.users.models import AbakusGroup, Membership, Penalty, User


class AbakusGroupTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'development_interest_groups.yaml']

    def setUp(self):
        self.non_committee = AbakusGroup(name='testgroup')
        self.non_committee.save()

    def test_is_commitee(self):
        committee = AbakusGroup.objects.get(name='Webkom')
        self.assertTrue(committee.is_committee)
        self.assertFalse(self.non_committee.is_committee)

    def test_is_interest_group(self):
        interest_group = InterestGroup.objects.get(name='AbaBrygg')
        self.assertTrue(interest_group.is_interest_group)
        self.assertFalse(self.non_committee.is_interest_group)

    def test_is_social_group(self):
        committee = AbakusGroup.objects.get(name='Webkom')
        interest_group = AbakusGroup.objects.get(name='AbaBrygg')
        self.assertTrue(committee.is_social_group)
        self.assertTrue(interest_group.is_social_group)
        self.assertFalse(self.non_committee.is_social_group)

    def test_natural_key(self):
        found_group = AbakusGroup.group_objects.get_by_natural_key(self.non_committee.name)
        self.assertEqual(self.non_committee, found_group)


class AbakusGroupHierarchyTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml']

    def setUp(self):
        self.abakom = AbakusGroup.objects.get(name='Abakom')

    def test_find_all_children(self):
        committees = AbakusGroup.objects.filter(parent=self.abakom.pk)
        children = self.abakom.get_children()
        self.assertEqual(len(committees), len(children))

    def test_abakom_is_root(self):
        abakus = AbakusGroup.objects.get(name='Abakus')
        self.assertTrue(abakus.is_root_node())

    def test_get_ancestors(self):
        abakus = AbakusGroup.objects.get(name='Abakus')
        webkom = AbakusGroup.objects.get(name='Webkom')

        ancestors = set(webkom.get_ancestors())

        self.assertEqual(len(ancestors), 2)
        self.assertTrue(abakus in ancestors)
        self.assertTrue(self.abakom in ancestors)

    def test_get_ancestors_include_self(self):
        abakus = AbakusGroup.objects.get(name='Abakus')
        webkom = AbakusGroup.objects.get(name='Webkom')

        ancestors = set(webkom.get_ancestors(include_self=True))

        self.assertEqual(len(ancestors), 3)
        self.assertTrue(webkom in ancestors)
        self.assertTrue(abakus in ancestors)
        self.assertTrue(self.abakom in ancestors)

    def test_get_descendants(self):
        webkom = AbakusGroup.objects.get(name='Webkom')
        first = AbakusGroup.objects.create(name='first', parent=webkom)
        second = AbakusGroup.objects.create(name='second', parent=first)

        descendants = webkom.get_descendants()
        self.assertEqual(len(descendants), 2)
        self.assertTrue(first in descendants)
        self.assertTrue(second in descendants)

    def test_get_descendants_include_self(self):
        abakus = AbakusGroup.objects.get(name='Abakus')
        self.assertEqual(set(AbakusGroup.objects.all()),
                         set(abakus.get_descendants(include_self=True)))


class UserTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'development_interest_groups.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_full_name(self):
        full_name = '{0} {1}'.format(self.user.first_name, self.user.last_name)
        self.assertEqual(full_name, self.user.get_full_name())

    def test_short_name(self):
        self.assertEqual(self.user.get_short_name(), self.user.first_name)

    def test_all_groups(self):
        abakus = AbakusGroup.objects.get(name='Abakus')
        abakom = AbakusGroup.objects.get(name='Abakom')
        webkom = AbakusGroup.objects.get(name='Webkom')

        webkom.add_user(self.user)
        abakus_groups = self.user.all_groups

        self.assertEqual(len(abakus_groups), 3)
        self.assertTrue(webkom in abakus_groups)
        self.assertTrue(abakom in abakus_groups)
        self.assertTrue(abakus in abakus_groups)

    def test_interest_groups(self):
        interest_group = AbakusGroup.objects.get(name='AbaBrygg')
        interest_group.add_user(self.user)
        interest_groups = self.user.interest_groups

        self.assertEqual(len(interest_groups), 1)
        self.assertTrue(interest_group in interest_groups)

    def test_social_groups(self):
        interest_group = AbakusGroup.objects.get(name='AbaBrygg')
        interest_group.add_user(self.user)
        commitee = AbakusGroup.objects.get(name='Webkom')
        commitee.add_user(self.user)
        social_groups = self.user.social_groups

        self.assertEqual(len(social_groups), 2)
        self.assertTrue(interest_group in social_groups)
        self.assertTrue(commitee in social_groups)

    def test_number_of_users(self):
        abakus = AbakusGroup.objects.get(name='Abakus')
        abakom = AbakusGroup.objects.get(name='Abakom')
        webkom = AbakusGroup.objects.get(name='Webkom')

        abakus.add_user(self.user)
        abakom.add_user(User.objects.get(pk=2))
        webkom.add_user(User.objects.get(pk=3))

        self.assertEqual(abakus.number_of_users, 3)
        self.assertEqual(abakom.number_of_users, 2)
        self.assertEqual(webkom.number_of_users, 1)

    def test_add_remove_user(self):
        abakus = AbakusGroup.objects.get(name='Abakus')

        abakus.add_user(self.user)
        self.assertEqual(abakus.number_of_users, 1)

        abakus = AbakusGroup.objects.get(name='Abakus')
        abakus.remove_user(self.user)
        self.assertEqual(abakus.number_of_users, 0)

    def test_add_user_to_two_groups(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.user)
        self.assertEqual(AbakusGroup.objects.get(name='Abakus').number_of_users, 1)
        self.assertEqual(AbakusGroup.objects.get(name='Webkom').number_of_users, 0)

        AbakusGroup.objects.get(name='Webkom').add_user(self.user)
        self.assertEqual(AbakusGroup.objects.get(name='Abakus').number_of_users, 1)
        self.assertEqual(AbakusGroup.objects.get(name='Webkom').number_of_users, 1)

    def test_natural_key(self):
        found_user = User.objects.get_by_natural_key(self.user.username)
        self.assertEqual(self.user, found_user)


class MembershipTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.test_committee = AbakusGroup.objects.get(name='Webkom')
        self.test_user = User.objects.get(pk=1)
        self.test_membership = Membership(
            user=self.test_user,
            abakus_group=self.test_committee,
            role=Membership.TREASURER
        )
        self.test_membership.save()

    def test_to_string(self):
        self.assertEqual(
            str(self.test_membership),
            '{0} is {1} in {2}'.format(
                self.test_membership.user,
                self.test_membership.get_role_display(),
                self.test_membership.abakus_group
            )
        )

    def test_natural_key(self):
        found_membership = Membership.objects.get_by_natural_key(self.test_user.username,
                                                                 self.test_committee.name)
        self.assertEqual(self.test_membership, found_membership)


class PenaltyTestCase(TestCase):
    fixtures = ['test_users.yaml', 'initial_abakus_groups.yaml', 'test_events.yaml']

    def setUp(self):
        self.test_user = User.objects.get(pk=1)
        self.source = Event.objects.all().first()

    def fake_time(self, y, m, d):
        dt = timezone.datetime(y, m, d)
        dt = timezone.pytz.timezone('UTC').localize(dt)
        return dt

    def test_create_penalty(self):
        penalty = Penalty.objects.create(user=self.test_user, reason='test',
                                         weight=1, source_event=self.source)

        self.assertEqual(self.test_user.number_of_penalties(), 1)
        self.assertEqual(self.test_user, penalty.user)
        self.assertEqual('test', penalty.reason)
        self.assertEqual(1, penalty.weight)
        self.assertEqual(self.source, penalty.source_event)
        self.assertEqual(self.source.id, penalty.source_event.id)

    def test_count_weights(self):
        weights = [1, 2]
        for weight in weights:
            Penalty.objects.create(user=self.test_user, reason='test',
                                   weight=weight, source_event=self.source)

        self.assertEqual(self.test_user.number_of_penalties(), sum(weights))

    def test_only_count_active_penalties(self):
        with mock.patch('django.utils.timezone.now', return_value=self.fake_time(2016, 10, 1)):
            Penalty.objects.create(created_at=timezone.now()-timedelta(days=20),
                                   user=self.test_user, reason='test', weight=1,
                                   source_event=self.source)
            Penalty.objects.create(created_at=timezone.now()-timedelta(days=19,
                                                                       hours=23,
                                                                       minutes=59),
                                   user=self.test_user, reason='test', weight=1,
                                   source_event=self.source)
            self.assertEqual(self.test_user.number_of_penalties(), 1)

    def test_frozen_penalties_count_as_active_winter(self):
        with mock.patch('django.utils.timezone.now', return_value=self.fake_time(2016, 12, 10)), \
                override_settings(PENALTY_IGNORE_WINTER=((12, 10), (1, 10))):

            # This penalty is created slightly less than 20 days from the freeze-point.
            # It should be counted as active.
            Penalty.objects.create(created_at=timezone.now()-timedelta(days=19,
                                                                       hours=23,
                                                                       minutes=59),
                                   user=self.test_user, reason='active', weight=1,
                                   source_event=self.source)

            # This penalty is created exactly 20 days from the freeze-point.
            # It should be counted as inactive.
            Penalty.objects.create(created_at=timezone.now()-timedelta(days=20),
                                   user=self.test_user, reason='inactive', weight=1,
                                   source_event=self.source)

            self.assertEqual(self.test_user.number_of_penalties(), 1)
            self.assertEqual(self.test_user.penalties.valid().first().reason, 'active')

    def test_frozen_penalties_count_as_active_summer(self):
        with mock.patch('django.utils.timezone.now', return_value=self.fake_time(2016, 6, 12)),\
                override_settings(PENALTY_IGNORE_SUMMER=((6, 12), (8, 15))):

            # This penalty is created slightly less than 20 days from the freeze-point.
            # It should be counted as active.
            Penalty.objects.create(created_at=timezone.now()-timedelta(days=19,
                                                                       hours=23,
                                                                       minutes=59),
                                   user=self.test_user, reason='active', weight=1,
                                   source_event=self.source)

            # This penalty is created exactly 20 days from the freeze-point.
            # It should be counted as inactive.
            Penalty.objects.create(created_at=timezone.now()-timedelta(days=20),
                                   user=self.test_user, reason='inactive', weight=1,
                                   source_event=self.source)

            self.assertEqual(self.test_user.number_of_penalties(), 1)
            self.assertEqual(self.test_user.penalties.valid().first().reason, 'active')
