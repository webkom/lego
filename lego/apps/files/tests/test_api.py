from unittest import mock

from rest_framework import status
from rest_framework.reverse import reverse

from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


class ListArticlesTestCase(BaseAPITestCase):
    fixtures = ["test_users.yaml"]

    url = "/api/v1/files/"

    def setUp(self):
        self.user = User.objects.first()

    def test_post_file_no_auth(self):
        res = self.client.post(f"{self.url}")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_no_key(self):
        self.client.force_authenticate(self.user)
        res = self.client.post(f"{self.url}", data={})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch("lego.apps.files.models.File.create_file")
    def test_post_create_file_call(self, mock_create_file):
        self.client.force_authenticate(self.user)
        key = "myfile.png"
        try:
            self.client.post(f"{self.url}", data={"key": key})
        except Exception:
            pass
        mock_create_file.assert_not_called()

        try:
            self.client.post(f"{self.url}", data={"key": key, "public": True})
        except Exception:
            pass
        mock_create_file.assert_called_with(key, self.user, True)

        try:
            self.client.post(f"{self.url}", data={"key": key, "public": False})
        except Exception:
            pass
        mock_create_file.assert_called_with(key, self.user, False)


def _get_detail_url(key):
    return reverse("api:v1:files-imagegallery", kwargs={"key": key})


class SetSaveForUserTest(BaseAPITestCase):
    fixtures = ["test_users.yaml", "test_files.yaml", "test_abakus_groups.yaml"]
    key = "abakus.png"
    token = "token"
    url = _get_detail_url(key)

    def setUp(self):
        self.webkom_user = User.objects.get(pk=9)
        self.user_no_perms = User.objects.get(pk=1)
        self.bedkom_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name="Webkom").add_user(self.webkom_user)
        AbakusGroup.objects.get(name="Bedkom").add_user(self.bedkom_user)

    def test_update_file_no_auth(self):
        res = self.client.patch(f"{self.url}", data={})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_file_no_token(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": True,
                "token": "wrgon_token",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_file_success(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": True,
                "token": self.token,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_file_success_bedkom(self):
        self.client.force_authenticate(self.bedkom_user)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": True,
                "token": self.token,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_file_bedkom_no_value(self):
        self.client.force_authenticate(self.bedkom_user)
        res = self.client.patch(
            f"{self.url}",
            data={
                "token": self.token,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_file_bedkom_bad_value(self):
        self.client.force_authenticate(self.bedkom_user)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": "1",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_file_bad_url(self):
        self.client.force_authenticate(self.webkom_user)
        res = self.client.patch(
            "/api/v1/files/error.png/set_save_for_use/",
            data={
                "token": self.token,
                "save_for_use": True,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_file_no_event_perm(self):
        self.client.force_authenticate(self.user_no_perms)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": True,
                "token": self.token,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_file_no_event_perm_no_token(self):
        self.client.force_authenticate(self.user_no_perms)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": True,
                "token": "wrong_token",
            },
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_file_no_auth_correct_token(self):
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": True,
                "token": self.token,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_file_set_false_bedkom(self):
        self.client.force_authenticate(self.bedkom_user)
        res = self.client.patch(
            f"{self.url}",
            data={
                "save_for_use": False,
                "token": self.token,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
