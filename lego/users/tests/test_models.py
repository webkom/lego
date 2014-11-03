# -*- coding: utf8 -*-
from django.test import TestCase
from lego.users.models import AbakusGroup, User, Membership


class GroupTestCase(TestCase):
    fixtures = ['initial_groups.yaml']

    def setUp(self):
        self.non_committee = AbakusGroup(name='testgroup')
        self.non_committee.save()

    def test_is_commitee(self):
        committee = AbakusGroup.objects.get(name='Webkom')
        self.assertTrue(committee.is_committee)
        self.assertFalse(self.non_committee.is_committee)


class UserTestCase(TestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_full_name(self):
        full_name = '{0} {1}'.format(self.user.first_name, self.user.last_name)
        self.assertEqual(full_name, self.user.get_full_name())

    def test_short_name(self):
        self.assertEqual(self.user.get_short_name(), self.user.first_name)


class MembershipTestCase(TestCase):
    fixtures = ['initial_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.test_committee = AbakusGroup.objects.get(name='Webkom')
        self.test_user = User.objects.get(pk=1)
        self.test_membership = Membership(
            user=self.test_user,
            group=self.test_committee,
            role=Membership.TREASURER
        )
        self.test_membership.save()

    def test_to_string(self):
        self.assertEqual(
            str(self.test_membership),
            '{0} is {1} in {2}'.format(
                self.test_membership.user,
                self.test_membership.get_role_display(),
                self.test_membership.group
            )
        )
