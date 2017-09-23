from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.users.models import User


class SiteMetaViewSetTestCase(APITestCase):

    fixtures = ['test_users.yaml']

    def setUp(self):
        self.url = '/api/v1/site-meta/'

    def test_access_without_auth(self):
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)

    def test_access_with_user(self):
        self.client.force_login(User.objects.first())
        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_200_OK, response.status_code)
