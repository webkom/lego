from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.restricted.models import RestrictedMail
from lego.apps.users.models import AbakusGroup, User


class RestrictedViewTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml', 'test_restricted_mails.yaml']

    def setUp(self):
        self.url = '/api/v1/restricted-mail/'
        self.allowed_user = User.objects.get(username='test1')
        self.denied_user = User.objects.get(username='test2')
        AbakusGroup.objects.get(name='Webkom').add_user(self.allowed_user)

    def test_list(self):
        """List instances created_by authenticated user only."""
        self.client.force_login(self.allowed_user)

        response = self.client.get(self.url)
        self.assertEquals(len(response.data['results']), 1)

    def test_list_no_perms(self):
        """A user tries to list with no permissions"""
        self.client.force_login(self.denied_user)

        response = self.client.get(self.url)
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_get_token_valid_instance(self):
        """Return a token file for a valid instance"""
        token = RestrictedMail.objects.get(id='1').token_query_param()

        response = self.client.get(f'{self.url}1/token/?auth={token}')
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals('attachment; filename="token"', response['Content-Disposition'])

        content = response.content.decode()
        self.assertEquals('LEGOTOKENtoken', content)

    def test_get_token_no_auth(self):
        """Return 401 on invalid token"""
        response = self.client.get(f'{self.url}1/token/?auth=invalid')
        self.assertEquals(status.HTTP_401_UNAUTHORIZED, response.status_code)
