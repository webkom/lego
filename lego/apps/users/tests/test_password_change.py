from django.contrib.auth import authenticate
from rest_framework import status

from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


class TestPasswordChange(BaseAPITestCase):
    fixtures = ["test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        self.url = "/api/v1/password-change/"

    def test_not_authenticated(self):
        response = self.client.post(
            self.url,
            {"password": "test", "newPassword": "test1", "retypeNewPassword": "test1"},
        )
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_invalid_password(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            {"password": "error", "newPassword": "test1", "retypeNewPassword": "test1"},
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_not_equal_new_passwords(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            {
                "password": "test",
                "newPassword": "not_equal_as_retype",
                "retypeNewPassword": "not_equal_new_password",
            },
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_new_password_not_valid(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, {"password": "test", "newPassword": "x", "retypeNewPassword": "x"}
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_new_password_success(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url,
            {
                "password": "test",
                "newPassword": "new_secret_password123",
                "retypeNewPassword": "new_secret_password123",
            },
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertTrue(
            authenticate(username="test1", password="new_secret_password123")
        )
