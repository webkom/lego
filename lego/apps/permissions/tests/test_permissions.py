from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from lego.apps.permissions.tests.models import TestModel
from lego.apps.permissions.tests.view import TestViewSet
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


class PermissionTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    test_update_object = {"name": "new_test_object"}

    def setUp(self):
        self.regular_users = User.objects.all()
        self.creator = self.regular_users[0]

        self.allowed_user = self.regular_users[1]
        self.disallowed_user = self.regular_users[2]
        self.webkom = AbakusGroup.objects.get(name="Webkom")
        self.webkom.add_user(self.allowed_user)

        self.test_object = TestModel(name="test_object", require_auth=True)
        self.test_object.save(current_user=self.creator)
        self.test_object.can_edit_users.add(self.allowed_user)
        self.test_object.can_view_groups.add(self.webkom)

        self.factory = APIRequestFactory()

    def test_create_successful(self):
        """
        Object permissions shouldn't stop users from creating objects, as that's handled by
        model permissions.
        """
        self.webkom.add_user(self.disallowed_user)
        request = self.factory.post("/permissiontest/", self.test_update_object)
        force_authenticate(request, self.disallowed_user)
        view = TestViewSet.as_view({"post": "create"})

        response = view(request)
        created = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created["name"], self.test_update_object["name"])

    def test_retrieve_successful(self):
        request = self.factory.get("/permissiontest/")
        force_authenticate(request, self.allowed_user)
        view = TestViewSet.as_view({"get": "retrieve"})

        response = view(request, pk=self.test_object.pk)
        test_object = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_object["name"], self.test_object.name)

    def test_retrieve_unsuccessful(self):
        request = self.factory.get("/permissiontest/")
        force_authenticate(request, self.disallowed_user)
        view = TestViewSet.as_view({"get": "retrieve"})

        response = view(request, pk=self.test_object.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_without_auth(self):
        shown_object = TestModel(name="shown", require_auth=False)
        shown_object.save(current_user=self.creator)

        request = self.factory.get("/permissiontest/")
        view = TestViewSet.as_view({"get": "list"})

        response = view(request)
        test_objects = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(test_objects), 1)
        self.assertEqual(test_objects[0]["name"], shown_object.name)

    def test_list_with_auth(self):
        hidden_object = TestModel(name="additional test")
        hidden_object.save(current_user=self.creator)

        request = self.factory.get("/permissiontest/")
        force_authenticate(request, self.allowed_user)
        view = TestViewSet.as_view({"get": "list"})

        response = view(request)
        test_objects = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(test_objects), 2)

    def test_edit_successful(self):
        request = self.factory.put("/permissiontest/", self.test_update_object)
        force_authenticate(request, self.allowed_user)
        view = TestViewSet.as_view({"put": "update"})

        response = view(request, pk=self.test_object.pk)
        edited_object = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(edited_object["name"], self.test_update_object["name"])

    def test_edit_unsuccessful(self):
        request = self.factory.put("/permissiontest/", self.test_update_object)
        force_authenticate(request, self.disallowed_user)
        view = TestViewSet.as_view({"put": "update"})

        response = view(request, pk=self.test_object.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_own(self):
        request = self.factory.put("/permissiontest/", self.test_update_object)
        force_authenticate(request, self.creator)
        view = TestViewSet.as_view({"put": "update"})

        response = view(request, pk=self.test_object.pk)
        edited_object = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(edited_object["name"], self.test_update_object["name"])

    def test_delete_successful(self):
        request = self.factory.delete("/permissiontest/")
        force_authenticate(request, self.allowed_user)
        view = TestViewSet.as_view({"delete": "destroy"})

        response = view(request, pk=self.test_object.pk)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_unsuccessful(self):
        self.test_object.can_view_groups.add(self.webkom)

        request = self.factory.delete("/permissiontest/")
        force_authenticate(request, self.disallowed_user)
        view = TestViewSet.as_view({"delete": "destroy"})

        response = view(request, pk=self.test_object.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_object_with_require_auth_false(self):
        """
        Editing an object with require_auth=False should not be possible
        """
        self.test_object.require_auth = False
        self.test_object.save()
        response = self.client.put(
            f"/permissiontest/{self.test_object.id}/", self.test_update_object
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
