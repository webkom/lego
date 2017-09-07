from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.users.models import User


class TestPasswordChange(APITestCase):

    fixtures = ['test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(username='test1')
        self.url = '/api/v1/password-change/'

    def test_not_authenticated(self):
        response = self.client.post(self.url, {
            'password': 'test',
            'new_password': 'test1',
            'retype_new_password': 'test1'
        })
        self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_invalid_password(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'password': 'error',
            'new_password': 'test1',
            'retype_new_password': 'test1'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_not_equal_new_passwords(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'password': 'test',
            'new_password': 'not_equal_as_retype',
            'retype_new_password': 'not_equal_new_password'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_new_password_not_valid(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'password': 'test',
            'new_password': 'x',
            'retype_new_password': 'x'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_new_password_success(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'password': 'test',
            'new_password': 'new_secret_password123',
            'retype_new_password': 'new_secret_password123'
        })
        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertTrue(authenticate(username='test1', password='new_secret_password123'))
