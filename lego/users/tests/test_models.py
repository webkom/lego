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


class GroupHierarchyTestcase(TestCase):
    fixtures = ['initial_groups.yaml']

    def setUp(self):
        self.abakom = AbakusGroup.objects.get(name='Abakom')

    def test_find_all_children(self):
        committees = AbakusGroup.objects.filter(parent=1)
        children = self.abakom.get_children()
        self.assertEqual(len(committees), len(children))

    def test_abakom_is_root(self):
        self.assertTrue(self.abakom.is_root_node())

    def test_get_descendants(self):
        webkom = AbakusGroup.objects.get(name='Webkom')
        under_webkom = AbakusGroup(name='under_group', parent=webkom)
        under_webkom.save()
        descendant = webkom.get_descendants()[0]
        self.assertEqual(under_webkom, descendant)


class UserTestCase(TestCase):
    fixtures = ['test_users.yaml']

    def test_full_name(self):
        user = User.objects.get(pk=1)
        full_name = '{0} {1}'.format(user.first_name, user.last_name)
        self.assertEqual(full_name, user.get_full_name())


class MembershipTestCase(TestCase):
    fixtures = ['initial_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.test_committee = AbakusGroup.objects.get(name='Webkom')
        self.test_user = User.objects.get(pk=1)
        self.test_membership = Membership(
            user=self.test_user,
            group=self.test_committee,
            title='The Best Test User',
        )

    def test_permission_status(self):
        self.assertEqual(self.test_membership.permission_status, Membership.MEMBER)
