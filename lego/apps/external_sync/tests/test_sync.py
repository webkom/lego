from unittest import mock

from django.test import TestCase

from lego.apps.external_sync.sync import Sync
from lego.apps.users.models import AbakusGroup, User


class SyncTestCase(TestCase):
    """
    This is a simple smoke test, it just makes sure all methods on the system classes is being
    called.
    """

    @mock.patch('lego.apps.external_sync.sync.LDAPSystem')
    def setUp(self, ldap_mock):
        self.users = User.objects.all()
        self.groups = AbakusGroup.objects.all()

        self.system_mock = mock.Mock()
        self.sync = Sync()
        self.sync.systems = [self.system_mock]

        self.sync.lookup_querysets = mock.Mock()
        self.sync.lookup_querysets.return_value = self.users, self.groups

    def test_run_sync(self):
        """Call sync and make sure correct functions is called."""
        self.system_mock.filter_users.return_value = self.users
        self.system_mock.filter_groups.return_value = self.groups

        self.sync.sync()

        self.system_mock.filter_users.assert_called_once_with(self.users)
        self.system_mock.filter_groups.assert_called_once_with(self.groups)

        self.system_mock.sync_users.assert_called_once_with(self.users)
        self.system_mock.sync_groups.assert_called_once_with(self.groups)

        self.system_mock.delete_excess_groups.assert_called_once_with(self.groups)
        self.system_mock.delete_excess_users.assert_called_once_with(self.users)
