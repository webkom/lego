from django.conf import settings
from rest_framework import status

from lego.utils.test_utils import BaseTestCase


class VersionRedirectTestCase(BaseTestCase):
    def test_redirect(self):
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(settings.API_VERSION in response.url)

    def test_404(self):
        response = self.client.get("/api/bad-url/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_default_router_redirect(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn(settings.API_VERSION, response.url)
