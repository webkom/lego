from django.db import IntegrityError
from django.test import TestCase

from lego.apps.email.models import EmailAddress, EmailList
from lego.apps.users.models import AbakusGroup, User


class EmailAddressTestCase(TestCase):

    fixtures = ['test_email_addresses.yaml', 'test_email_lists.yaml']

    def test_create_duplicate(self):
        """Only one instance of the address is allowed."""
        self.assertRaises(IntegrityError, EmailAddress.objects.create, email='address')

    def test_is_assigned_when_used_by_list(self):
        """The is_Assigned function returns True when the address is used by an EmailList."""
        address = EmailAddress.objects.get(email='address')
        self.assertTrue(address.is_assigned())

        list = EmailList.objects.get(id=1)
        self.assertFalse(address.is_assigned(list))

    def test_is_assigned_when_not_used(self):
        """is_assigned returns False when the address is'nt used."""
        address = EmailAddress.objects.get(email='address1')
        self.assertFalse(address.is_assigned())


class EmailListTestCase(TestCase):

    fixtures = ['initial_files.yaml', 'initial_abakus_groups.yaml',
                'test_email_addresses.yaml', 'test_users.yaml', 'test_email_lists.yaml']

    def test_email_address(self):
        """email_address should return the full address."""
        list = EmailList.objects.get(id=1)

        self.assertEqual('address@abakus.no', list.email_address)

    def test_members(self):
        """The members function returns a list of user emails"""
        list = EmailList.objects.get(id=1)

        user = User.objects.get(username='test1')
        group = AbakusGroup.objects.get(name='Students')

        group_user = User.objects.get(username='test2')
        under_group = AbakusGroup.objects.get(name='Datateknologi')
        under_group.add_user(group_user)

        list.users.add(user)
        list.groups.add(group)

        self.assertSequenceEqual(
            {'test1@user.com', 'test2@user.com'},
            set(list.members())
        )
