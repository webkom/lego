from lego.apps.permissions.constants import EDIT
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.apps.permissions.tests.models import TestModel
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseTestCase


class ObjectPermissionsModelTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def assertFieldsEqual(self, expected, actual):
        expected_deconstructed = {
            ":".join(field.deconstruct()[0:2]) for field in expected
        }
        actual_deconstructed = {":".join(field.deconstruct()[0:2]) for field in actual}
        self.assertSetEqual(expected_deconstructed, actual_deconstructed)

    def setUp(self):
        self.regular_users = User.objects.all()
        self.creator = self.regular_users[0]

        self.test_object = TestModel(name="test_object")
        self.test_object.save(current_user=self.creator)

    def test_inheritance(self):
        mixin_fields = set(ObjectPermissionsModel._meta.get_fields())
        test_fields = set(TestModel._meta.get_fields())
        correct_fields = list(mixin_fields.union(test_fields))
        fields = TestModel._meta.get_fields()

        self.assertFieldsEqual(correct_fields, fields)

    def test_can_edit_users(self):
        can_edit_user = self.regular_users[1]
        cant_edit_user = self.regular_users[2]

        self.test_object.can_edit_users.add(can_edit_user)

        self.assertTrue(can_edit_user.has_perm(EDIT, self.test_object))
        self.assertFalse(cant_edit_user.has_perm(EDIT, self.test_object))

    def test_can_edit_groups_hierarchy(self):
        user = self.regular_users[1]
        abakom = AbakusGroup.objects.get(name="Abakom")
        webkom = AbakusGroup.objects.get(name="Webkom")
        webkom.add_user(user)

        self.test_object.can_edit_groups.add(abakom)

        self.assertTrue(user.has_perm(EDIT, self.test_object))
