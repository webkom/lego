# -*- coding: utf8 -*-
from django.test import TestCase

from lego.users.models import AbakusGroup, User


class AbakusBackendTestCase(TestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.test_user = User.objects.get(username='useradmin_test')
        self.useradmin_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_group.add_user(self.test_user)

    def test_has_perm_exact(self):
        has_perm = self.test_user.has_perm('/sudo/admin/users/list/')
        self.assertTrue(has_perm)

    def test_has_perm_starts_with_correct(self):
        new_group = AbakusGroup.objects.create(name='new', permissions=['/sudo/admin/'])
        new_group.add_user(self.test_user)
        self.assertTrue(self.test_user.has_perm('/sudo/admin/does/not/exist'))

    def test_has_perm_incorrect(self):
        has_perm = self.test_user.has_perm('/sudo')
        self.assertFalse(has_perm)
