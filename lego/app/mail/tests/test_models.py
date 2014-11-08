# -*- coding: utf8 -*-
from django.test import TestCase
from django.core.validators import ValidationError
from django.utils import timezone

from lego.app.mail.models import UserMapping, GroupMapping, OneTimeMapping
from lego.users.models import User
from lego.users.models import AbakusGroup


class AddressTestCase(TestCase):
    fixtures = ['test_users.yaml']

    def test_local_part(self):
        user = User.objects.get(pk=1)
        mapping = UserMapping(address='!#$%*/?^`{|}~€', user=user)
        self.assertRaises(ValidationError, mapping.save)

    def test_lower_local_part(self):
        user = User.objects.get(pk=1)
        mapping = UserMapping(address='WebKom', user=user)
        mapping.save()
        self.assertEqual(mapping.address, 'webkom')
        self.assertNotEquals(mapping.address, 'WebKom')


class UserMappingTestCase(TestCase):
    fixtures = ['test_users.yaml', 'test_user_mappings.yaml']

    def test_user_mapping(self):
        user = User.objects.get(pk=1)
        mapping = UserMapping.objects.get(pk=1)
        self.assertEquals(mapping.user, user)
        self.assertEquals(mapping.address, 'testuser1mapping1')
        self.assertEquals(mapping.get_recipients()[0], user.email)

    def test_user_reverse(self):
        user = User.objects.get(pk=1)
        mappings = user.mail_mappings.all()
        for mapping in mappings:
            self.assertEquals(mapping.user, user)
            self.assertIn(mapping.address, ['testuser1mapping1', 'testuser1mapping2'])
            self.assertEquals(mapping.get_recipients()[0], user.email)


class GroupMappingTestCase(TestCase):
    fixtures = ['test_users.yaml', 'initial_groups.yaml', 'test_group_mappings.yaml']

    def test_group_mapping(self):
        group_mapping = GroupMapping.objects.get(address='webkom')
        recipients = group_mapping.get_recipients()
        for recipient in recipients:
            self.assertIn(recipient, ['test1@user.com', 'test2@user.com'])
            self.assertNotEqual(recipient, 'super@user.com')

    def test_additional_user(self):
        group_mapping = GroupMapping.objects.get(address='webkom')
        user_to_add = User.objects.get(pk=3)
        group_mapping.additional_users.add(user_to_add)
        group_mapping.save()
        for recipient in group_mapping.get_recipients():
            self.assertIn(recipient, ['test1@user.com', 'test2@user.com', 'super@user.com'])


class OneTimeMappingTestCase(TestCase):
    fixtures = ['test_users.yaml', 'initial_groups.yaml']

    # TODO: Test generic model malling, needs a model that implements the GenericMappingMixin mixin

    def setUp(self):
        one_time_mapping = OneTimeMapping.objects.create(from_address='otm@site.com')
        one_time_mapping.save()

    def test_one_time_mapping_creation(self):
        one_time_mapping = OneTimeMapping.objects.get(from_address='otm@site.com')
        self.assertEqual(one_time_mapping.from_address, 'otm@site.com')
        self.assertEqual(len(one_time_mapping.token), 36)

        self.assertEqual(one_time_mapping.is_valid, True)

        one_time_mapping.timeout = timezone.now()
        one_time_mapping.save()

        self.assertEqual(one_time_mapping.is_valid, False)

    def test_one_time_mapping_group(self):
        one_time_mapping = OneTimeMapping.objects.get(from_address='otm@site.com')
        group_to_add = AbakusGroup.objects.get(pk=1)
        group_to_add.add_user(User.objects.get(pk=1))
        group_to_add.save()
        one_time_mapping.groups.add(group_to_add)
        one_time_mapping.save()

        recipients = one_time_mapping.get_recipents()
        for recipient in recipients:
            self.assertEqual(recipient, 'test1@user.com')
