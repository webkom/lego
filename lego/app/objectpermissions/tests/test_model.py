# -*- coding: utf8 -*-
from django.test import TestCase
from lego.app.objectpermissions.models import ObjectPermissionsMixin
from lego.app.objectpermissions.tests.model import TestModel
from lego.users.models import User


class ObjectPermissionsModelTestCase(TestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.creator = User.objects.get(pk=1)
        self.test_object = TestModel(name='test_object')
        self.test_object.save(current_user=self.creator)

    def test_inheritance(self):
        mixin_fields = set(ObjectPermissionsMixin._meta.get_all_field_names())
        test_fields = set(TestModel._meta.get_all_field_names())
        correct_fields = mixin_fields.union(test_fields)
        fields = set(TestModel._meta.get_all_field_names())

        self.assertEqual(correct_fields, fields)

    def test_can_edit_users(self):
        can_edit_user = User.objects.get(pk=2)
        cant_edit_user = User.objects.get(pk=3)

        self.test_object.can_edit_users.add(can_edit_user)

        self.assertTrue(self.test_object.can_edit(can_edit_user))
        self.assertFalse(self.test_object.can_edit(cant_edit_user))
