from django.test import TestCase

from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.tests.models import TestModel
from lego.apps.users.models import AbakusGroup, User


class ObjectPermissionsModelTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.regular_users = User.objects.all()
        self.creator = self.regular_users[0]

        self.test_object = TestModel(name='test_object')
        self.test_object.save(current_user=self.creator)

    def test_inheritance(self):
        mixin_fields = set(ObjectPermissionsModel._meta.get_fields())
        test_fields = set(TestModel._meta.get_fields())
        correct_fields = mixin_fields.union(test_fields)
        fields = set(TestModel._meta.get_fields())

        self.assertEqual(correct_fields, fields)

    def test_can_edit_users(self):
        can_edit_user = self.regular_users[1]
        cant_edit_user = self.regular_users[2]

        self.test_object.can_edit_users.add(can_edit_user)

        self.assertTrue(self.test_object.can_edit(can_edit_user))
        self.assertFalse(self.test_object.can_edit(cant_edit_user))

    def test_can_edit_groups_hierarchy(self):
        user = self.regular_users[1]
        abakom = AbakusGroup.objects.get(name='Abakom')
        webkom = AbakusGroup.objects.get(name='Webkom')
        webkom.add_user(user)

        self.test_object.can_edit_groups.add(abakom)

        self.assertTrue(self.test_object.can_edit(user))
