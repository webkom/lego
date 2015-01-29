# -*- coding: utf8 -*-
from django.test import TestCase

from lego.users.models import AbakusGroup, User


class AbakusBackendTestCase(TestCase):
    fixtures = ['initial_permission_groups.yaml', 'test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.test_user = User.objects.get(username='useradmin_test')
        self.useradmin_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_group.add_user(self.test_user)

    def test_should_have_perm(self):
        has_perm = self.test_user.has_perm('users.add_user')
        self.assertTrue(has_perm)

    def test_should_not_have_perm(self):
        has_perm = self.test_user.has_perm('abakusgroup.create_abakusgroup')
        self.assertFalse(has_perm)
