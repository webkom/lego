from unittest import mock
from unittest.mock import call

from django.test import TestCase, override_settings

from lego.apps.external_sync.external import ldap
from lego.apps.users.models import AbakusGroup, User


class LDAPTestCase(TestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    @mock.patch('lego.apps.external_sync.external.ldap.LDAPLib')
    def setUp(self, ldap_mock):
        self.ldap = ldap.LDAPSystem()

    def test_migrate(self):
        """Make sure the org units is created"""
        self.ldap.migrate()
        self.ldap.ldap.update_organization_unit.assert_has_calls((call('users'), call('groups')))

    def test_filter_users(self):
        """Test1 is the only user with a ldap password hash"""
        filtered = self.ldap.filter_users(User.objects.all()).values_list('username', flat=True)
        self.assertListEqual(list(filtered), ['test1'])

    @override_settings(LDAP_GROUPS=['UserAdminTest'])
    def test_filter_groups(self):
        """Return groups with a name in the LDAP_GROUPS setting"""
        filtered = self.ldap.filter_groups(AbakusGroup.objects.all()).values_list('name', flat=True)
        self.assertListEqual(list(filtered), ['UserAdminTest'])

    def test_search_user(self):
        """Search for a user"""
        self.ldap.ldap.search_user.return_value = True

        user = User.objects.get(username='test1')
        self.assertTrue(self.ldap.user_exists(user))
        self.ldap.ldap.search_user.assert_called_once_with('test1')

    def test_add_user(self):
        """Make user the LDAPLib.ass_user is called with the correct arguments"""
        user = User.objects.get(username='test1')
        self.ldap.add_user(user)

        self.ldap.ldap.add_user.assert_called_once_with(
            user.username, user.first_name, user.last_name, user.email, user.ldap_password_hash
        )

    def test_update_user_correct_password(self):
        """
        The update user function is simple, but we makes sure the password change function is
        called if necessary
        """
        user = User.objects.get(username='test1')

        self.ldap.ldap.check_password.return_value = True
        self.ldap.update_user(user)
        self.ldap.ldap.change_password.assert_not_called()

        self.ldap.ldap.check_password.return_value = False
        self.ldap.update_user(user)
        self.ldap.ldap.change_password.assert_called_once_with(
            user.username, user.ldap_password_hash
        )

    def test_search_group(self):
        """Search for a group"""
        self.ldap.ldap.search_group.return_value = True

        group = AbakusGroup.objects.get(name='UserAdminTest')
        self.assertTrue(self.ldap.group_exists(group))
        self.ldap.ldap.search_group.assert_called_once_with(group.id)

    def test_add_group(self):
        """Make sure LDAPLib.add_group is called with the correct arguments"""
        group = AbakusGroup.objects.get(name='UserAdminTest')
        self.ldap.add_group(group)

        self.ldap.ldap.add_group.assert_called_once_with(group.id, group.name)

        members = list(group.memberships.values_list('user__username', flat=True))
        self.ldap.ldap.update_group_members.assert_called_once_with(group.name, members)

    def test_update_group(self):
        """Make sure memberships gets updated at group update"""
        group = AbakusGroup.objects.get(name='UserAdminTest')
        members = list(group.memberships.values_list('user__username', flat=True))

        self.ldap.update_group(group)
        self.ldap.ldap.update_group_members.assert_called_once_with(group.name, members)
