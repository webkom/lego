from django.test import Client, TestCase

from lego.apps.users.models import User


class APIDocsTestCase(TestCase):
    """
    Make sure the api docs works like expected.
    """
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.client = Client()

    def test_get_without_auth(self):
        response = self.client.get('/api-docs/')
        self.assertEquals(200, response.status_code)

    def test_get_with_auth(self):
        self.client.force_login(User.objects.get(username='test1'))
        response = self.client.get('/api-docs/')
        self.assertEquals(200, response.status_code)
