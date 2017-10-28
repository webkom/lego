from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.gallery.models import GalleryPicture
from lego.apps.users.models import AbakusGroup, User


@mock.patch('lego.apps.files.fields.storage.generate_signed_url', return_value='signed_url')
class GalleryViewSetTestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_files.yaml',
                'test_galleries.yaml', 'test_gallery_pictures.yaml']

    def setUp(self):
        self.permitted_user = User.objects.get(username='test1')
        self.read_only_user = User.objects.get(username='abakule')
        self.denied_user = User.objects.get(username='pleb')
        self.url = '/api/v1/galleries/'

        self.admin_group = AbakusGroup.objects.get(name='GalleryAdminTest')
        self.admin_group.add_user(self.permitted_user)
        self.read_group = AbakusGroup.objects.get(name='GalleryTest')
        self.read_group.add_user(self.read_only_user)

        self.add_picture_data = {
            'description': 'Test image',
            'file': 'abakus2.png:token',
            'active': True
        }

    def test_detail_gallery_permitted_user(self, mock_signer):
        """Permitted user should be able to see all pictures."""
        self.client.force_login(self.permitted_user)

        response = self.client.get(f'{self.url}1/pictures/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data['results']))

    def test_detail_gallery_read_user(self, mock_signer):
        """Read only user is able to fetch the gallery."""
        self.client.force_login(self.read_only_user)

        response = self.client.get(f'{self.url}1/pictures/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data['results']))

    def test_detail_gallery_denied(self, mock_signer):
        """Users is not able to fetch galleries by default."""
        self.client.force_login(self.denied_user)

        response = self.client.get(f'{self.url}1/')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_add_image_permitted(self, mock_signer):
        """The permitted user is able to add images"""
        self.client.force_login(self.permitted_user)

        response = self.client.post(f'{self.url}1/pictures/', self.add_picture_data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def test_add_picture_read_only_user(self, mock_signer):
        """The read_only_user user is not be able to add images."""
        self.client.force_login(self.read_only_user)

        response = self.client.post(f'{self.url}1/pictures/', self.add_picture_data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_picture_permitted(self, mock_signer):
        """The permitted user is able to delete pictures."""
        self.client.force_login(self.permitted_user)

        response = self.client.delete(f'{self.url}1/pictures/1/')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_edit_picture_permitted(self, mock_signer):
        """The permitted user is able to update pictures"""
        self.client.force_login(self.permitted_user)

        response = self.client.patch(f'{self.url}1/pictures/2/', {
            'active': True, 'description': 'Test description'
        })
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertTrue(GalleryPicture.objects.get(id=2).active)
