from unittest import mock

from rest_framework import status

from lego.apps.gallery.models import Gallery, GalleryPicture
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


@mock.patch(
    "lego.apps.files.fields.storage.generate_signed_url", return_value="signed_url"
)
class GalleryViewSetTestCase(BaseAPITestCase):

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_files.yaml",
        "test_galleries.yaml",
        "test_gallery_pictures.yaml",
    ]

    def setUp(self):
        self.permitted_user = User.objects.get(username="test1")
        self.read_only_user = User.objects.get(username="abakule")
        self.denied_user = User.objects.get(username="pleb")
        self.url = "/api/v1/galleries/"

        self.read_group = AbakusGroup.objects.get(name="GalleryTest")
        self.read_group.add_user(self.read_only_user)

        self.add_picture_data = {
            "description": "Test image",
            "file": "abakus2.png:token",
            "active": True,
        }

    def test_list_galleries_denied_user(self, mock_signer):
        """Permitted user should not be able to se the gallery."""
        self.client.force_authenticate(self.denied_user)

        response = self.client.get(f"{self.url}")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.json()["results"]))

    def test_list_galleries_permitted_user(self, mock_signer):
        """Permitted user should see the gallery."""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.get(f"{self.url}")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_detail_gallery_permitted_user(self, mock_signer):
        """Permitted user should be able to see all pictures."""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.get(f"{self.url}1/pictures/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.json()["results"]))

    def test_detail_gallery_read_user(self, mock_signer):
        """Read only user is able to fetch the gallery."""
        self.client.force_authenticate(self.read_only_user)

        response = self.client.get(f"{self.url}1/pictures/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_detail_gallery_no_user(self, mock_signer):
        """Non logged in users should not find any pictures"""
        response = self.client.get(f"{self.url}1/pictures/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.json()["results"]))

    def test_detail_gallery_denied(self, mock_signer):
        """Users is not able to fetch galleries by default."""
        self.client.force_authenticate(self.denied_user)

        response = self.client.get(f"{self.url}1/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_image_permitted(self, mock_signer):
        """The permitted user is able to add images"""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.post(f"{self.url}1/pictures/", self.add_picture_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_add_picture_read_only_user(self, mock_signer):
        """The read_only_user user is not be able to add images."""
        self.client.force_authenticate(self.read_only_user)

        response = self.client.post(f"{self.url}1/pictures/", self.add_picture_data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_add_picture_no_user(self, mock_signer):
        response = self.client.post(f"{self.url}1/pictures/", self.add_picture_data)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_picture_permitted(self, mock_signer):
        """The permitted user is able to delete pictures."""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.delete(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_view_picture_denied_user(self, mock_signer):
        """The permitted user is not able to view picture"""
        self.client.force_authenticate(self.denied_user)
        response = self.client.get(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_picture_no_user(self, mock_signer):
        """The picture is not available for non-authed users"""
        response = self.client.get(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_picture_permitted(self, mock_signer):
        """The permitted user is able to view the image."""
        self.client.force_authenticate(self.permitted_user)
        response = self.client.get(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_picture_permitted_read_only(self, mock_signer):
        """The permitted user is able to delete pictures."""
        self.client.force_authenticate(self.read_only_user)
        response = self.client.get(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_edit_picture_permitted(self, mock_signer):
        """The permitted user is able to update pictures"""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.patch(
            f"{self.url}1/pictures/2/",
            {"active": True, "description": "Test description"},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertTrue(GalleryPicture.objects.get(id=2).active)


@mock.patch(
    "lego.apps.files.fields.storage.generate_signed_url", return_value="signed_url"
)
class GalleryViewSetTestCaseRequireAuthFalse(BaseAPITestCase):

    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_files.yaml",
        "test_galleries.yaml",
        "test_gallery_pictures.yaml",
    ]

    def setUp(self):
        self.permitted_user = User.objects.get(username="test1")
        self.read_only_user = User.objects.get(username="abakule")
        self.denied_user = User.objects.get(username="pleb")
        self.url = "/api/v1/galleries/"

        self.read_group = AbakusGroup.objects.get(name="GalleryTest")
        self.read_group.add_user(self.read_only_user)

        self.add_picture_data = {
            "description": "Test image",
            "file": "abakus2.png:token",
            "active": True,
        }
        self.gallery = Gallery.objects.get(pk=1)
        self.gallery.require_auth = False
        self.gallery.save()

    def test_list_galleries_denied_user(self, mock_signer):
        """Permitted user should not be able to se the gallery."""
        self.client.force_authenticate(self.denied_user)

        response = self.client.get(f"{self.url}")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_list_galleries_permitted_user(self, mock_signer):
        """Permitted user should see the gallery."""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.get(f"{self.url}")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_detail_gallery_permitted_user(self, mock_signer):
        """Permitted user should be able to see all pictures."""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.get(f"{self.url}1/pictures/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.json()["results"]))

    def test_detail_gallery_read_user(self, mock_signer):
        """Read only user is able to fetch the gallery."""
        self.client.force_authenticate(self.read_only_user)

        response = self.client.get(f"{self.url}1/pictures/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_detail_gallery_no_user(self, mock_signer):
        """Non logged in users should find active pictures"""
        response = self.client.get(f"{self.url}1/pictures/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_active_picture_non_allowed_user(self, mock_signer):
        self.client.force_authenticate(self.denied_user)
        response = self.client.get(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_inactive_picture_non_allowed_user(self, mock_signer):
        self.client.force_authenticate(self.denied_user)
        response = self.client.get(f"{self.url}1/pictures/2/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_active_picture_non_allowed_no_user(self, mock_signer):
        response = self.client.get(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_inactive_picture_non_allowed_no_user(self, mock_signer):
        response = self.client.get(f"{self.url}1/pictures/2/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_detail_gallery_denied(self, mock_signer):
        self.client.force_authenticate(self.denied_user)

        response = self.client.get(f"{self.url}1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_detail_gallery_no_user_(self, mock_signer):
        """Non logged in user should be able to see gallery info."""
        response = self.client.get(f"{self.url}1/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_add_image_permitted(self, mock_signer):
        """The permitted user is able to add images"""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.post(f"{self.url}1/pictures/", self.add_picture_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_add_picture_read_only_user(self, mock_signer):
        """The read_only_user user is not be able to add images."""
        self.client.force_authenticate(self.read_only_user)

        response = self.client.post(f"{self.url}1/pictures/", self.add_picture_data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_add_picture_no_user(self, mock_signer):
        """Non logged in user is not be able to add images."""
        response = self.client.post(f"{self.url}1/pictures/", self.add_picture_data)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_picture_no_user(self, mock_signer):
        """Non logged i user is not able to delete pictures."""
        response = self.client.delete(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_delete_picture_permitted(self, mock_signer):
        """The permitted user is able to delete pictures."""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.delete(f"{self.url}1/pictures/1/")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_edit_picture_permitted2(self, mock_signer):
        """The permitted user is able to update pictures"""
        self.client.force_authenticate(self.read_only_user)

        response = self.client.patch(
            f"{self.url}1/pictures/1/",
            {"active": True, "description": "Test description"},
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_edit_picture_permitted(self, mock_signer):
        """The permitted user is able to update pictures"""
        self.client.force_authenticate(self.permitted_user)

        response = self.client.patch(
            f"{self.url}1/pictures/2/",
            {"active": True, "description": "Test description"},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertTrue(GalleryPicture.objects.get(id=2).active)


class GalleryViewSetMetadataTestCase(BaseAPITestCase):

    fixtures = ["test_abakus_groups.yaml", "test_users.yaml", "test_galleries.yaml"]

    def setUp(self):
        self.url = "/api/v1/galleries/"
        self.gallery = Gallery.objects.get(pk=1)

    def test_public_metadata(self):
        self.gallery.public_metadata = True
        self.gallery.save()
        response = self.client.get(f"{self.url}1/metadata/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()
        self.assertEqual(self.gallery.pk, data["id"])
        self.assertEqual(self.gallery.title, data["title"])
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_public_metadata_disabled(self):
        self.gallery.public_metadata = False
        self.gallery.save()
        response = self.client.get(f"{self.url}1/metadata/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
