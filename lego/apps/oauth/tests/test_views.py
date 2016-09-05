from oauth2_provider.models import AccessToken
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.users.models import AbakusGroup, Membership, User


class OauthViewsTestCase(APITestCase):

    fixtures = ['test_users.yaml', 'test_applications.yaml', 'test_access_tokens.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = '/api/v1/oauth2/access-tokens/'

    def test_list_tokens_no_auth(self):
        """Make sure a unauthenticated user not have access to the token view."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_tokens(self):
        """Make sure the user can access the token list and the list is filtered."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), AccessToken.objects.filter(user=self.user).count())
        for token in response.data:
            self.assertEqual(token['user'], self.user.id)

    def test_delete_token(self):
        """Make sure the client can delete a token. This is the same sa revoking it."""
        self.client.force_login(self.user)
        response = self.client.delete('{base_url}1/'.format(base_url=self.url))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_token_attached_to_different_user(self):
        """Make sure a user can't delete a token owned by a other user."""
        self.client.force_login(self.user)
        response = self.client.delete('{base_url}2/'.format(base_url=self.url))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OauthApplicationViewsTestCase(APITestCase):

    fixtures = ['test_users.yaml', 'test_abakus_groups.yaml', 'test_applications.yaml',
                'test_access_tokens.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)  # Normal user with no permissions
        self.url = '/api/v1/oauth2/applications/'

    def test_list_applications_no_auth(self):
        """Make sure permissions and authentication is required to display oauth applications.
        This is "sensitive" information"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_applications(self):
        """Make sure permitted users can list applications."""
        self.client.force_login(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(id=6)
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_application(self):
        """Make sure permitted users can create applications."""
        self.client.force_login(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(id=6)
        )

        application = {
            'name': 'Abakus APP',
            'description': 'Test oauth app',
            'user': 1,
            'redirectUris': '',
            'clientType': 'public',
            'authorizationGrantType': 'password',
            'skipAuthorization': False
        }
        response = self.client.post(self.url, application)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_application(self):
        """Make sure permitted users can delete applications."""
        self.client.force_login(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(id=6)
        )
        response = self.client.delete('{base_url}{object_id}/'.format(
            base_url=self.url, object_id=1
        ))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
