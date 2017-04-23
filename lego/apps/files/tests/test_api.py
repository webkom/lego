from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.users.models import User


class ListArticlesTestCase(APITestCase):
    fixtures = ['test_users.yaml']

    url = '/api/v1/files/'

    def setUp(self):
        self.user = User.objects.first()

    def test_post_file_no_auth(self):
        res = self.client.post(f'{self.url}')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_no_key(self):
        self.client.force_login(self.user)
        res = self.client.post(f'{self.url}', data={})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('lego.apps.files.models.File.create_file')
    def test_post_create_file_call(self, mock_create_file):
        self.client.force_login(self.user)
        key = 'myfile.png'
        try:
            self.client.post(f'{self.url}', data={'key': key})
        except Exception as e:
            pass
        mock_create_file.assert_not_called()

        try:
            self.client.post(f'{self.url}', data={'key': key, 'public': True})
        except Exception as e:
            pass
        mock_create_file.assert_called_with(key, self.user, True)

        try:
            self.client.post(f'{self.url}', data={'key': key, 'public': False})
        except Exception as e:
            pass
        mock_create_file.assert_called_with(key, self.user, False)
