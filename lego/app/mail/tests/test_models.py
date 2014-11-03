# -*- coding: utf8 -*-
from datetime import date
from django.test import TestCase
from lego.app.mail.models import UserMapping, GroupMapping, RawMapping, RawMappingElement, \
    GenericMapping, OneTimeMapping
from lego.users.models import User, AbakusGroup as Group, Membership


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

    def setUp(self):
        group = Group.objects.get(pk=9)
        user = User.objects.get(pk=1)
        membership = Membership(user=user, group=group, start_date=date.today())
        membership.save()

    def test_group_mapping(self):
        mapping = GroupMapping.objects.get(pk=1)
        group = Group.objects.get(pk=9)
        self.assertEquals(mapping.group, group)

        get_mapping = GroupMapping.objects.get(address='webkom')
        self.assertEquals(mapping, get_mapping)

        self.assertEquals(len(mapping.get_recipients()), 2)

        for recipient in mapping.get_recipients():
            self.assertIn(recipient, [User.objects.get(pk=1).email, User.objects.get(pk=2).email])


class RawMappingTestCase(TestCase):
    fixtures = ['test_raw_mappings.yaml']

    def setUp(self):
        pass

    def test_taw_mapping(self):
        raw_mapping = RawMapping.objects.get(pk=1)
        recipients = raw_mapping.get_recipients()
        self.assertEquals(len(recipients), 2)
        for recipient in recipients:
            self.assertIn(recipient, ['test1@abakus.no', 'test2@abakus.no'])
