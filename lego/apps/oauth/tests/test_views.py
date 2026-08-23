from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from oauth2_provider.models import AccessToken

from lego.apps.oauth.models import APIApplication
from lego.apps.users.models import AbakusGroup, Membership, User
from lego.utils.test_utils import BaseAPITestCase


class OauthViewsTestCase(BaseAPITestCase):
    fixtures = ["test_users.yaml", "test_applications.yaml", "test_access_tokens.yaml"]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = "/api/v1/oauth2-access-tokens/"

    def test_list_tokens_no_auth(self):
        """Make sure a unauthenticated user not have access to the token view."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_tokens(self):
        """Make sure the user can access the token list and the list is filtered."""
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            len(response.json()["results"]),
            AccessToken.objects.filter(user=self.user).count(),
        )
        for token in response.json()["results"]:
            self.assertEqual(token["user"], self.user.id)

    def test_delete_token(self):
        """Make sure the client can delete a token. This is the same sa revoking it."""
        self.client.force_authenticate(self.user)
        response = self.client.delete("{base_url}1/".format(base_url=self.url))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_token_attached_to_different_user(self):
        """Make sure a user can't delete a token owned by a other user."""
        self.client.force_authenticate(self.user)
        response = self.client.delete("{base_url}2/".format(base_url=self.url))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def _machine_token(self):
        application = APIApplication.objects.create(
            user=self.user,
            client_type=APIApplication.CLIENT_CONFIDENTIAL,
            authorization_grant_type=APIApplication.GRANT_CLIENT_CREDENTIALS,
            name="machine client",
        )
        return AccessToken.objects.create(
            application=application,
            user=None,
            token="machine-token",
            scope="all",
            expires=timezone.now() + timedelta(days=1),
        )

    def test_owner_can_list_and_revoke_machine_tokens(self):
        machine_token = self._machine_token()

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [token["id"] for token in response.json()["results"]]
        self.assertIn(machine_token.id, ids)

        response = self.client.delete(f"{self.url}{machine_token.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AccessToken.objects.filter(id=machine_token.id).exists())

    def test_machine_tokens_are_hidden_from_other_users(self):
        machine_token = self._machine_token()

        self.client.force_authenticate(User.objects.get(id=2))
        response = self.client.get(self.url)
        ids = [token["id"] for token in response.json()["results"]]
        self.assertNotIn(machine_token.id, ids)

        response = self.client.delete(f"{self.url}{machine_token.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OauthApplicationViewsTestCase(BaseAPITestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_applications.yaml",
        "test_access_tokens.yaml",
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)  # Normal user with no permissions
        self.url = "/api/v1/oauth2-applications/"

    def test_list_applications_no_auth(self):
        """Make sure permissions and authentication is required to display oauth applications.
        This is "sensitive" information"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_applications(self):
        """Make sure permitted users can list applications."""
        self.client.force_authenticate(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(name="APIApplicationTest"),
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_application(self):
        """Make sure permitted users can create applications."""
        self.client.force_authenticate(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(name="APIApplicationTest"),
        )

        application = {
            "name": "Abakus APP",
            "description": "Test oauth app",
            "user": 1,
            "redirectUris": "",
            "clientType": "public",
            "authorizationGrantType": "password",
            "skipAuthorization": False,
        }
        response = self.client.post(self.url, application)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_machine_application_cannot_be_edited(self):
        """The forced fields in the serializer would silently downgrade it."""
        self.client.force_authenticate(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(name="APIApplicationTest"),
        )
        machine = APIApplication.objects.create(
            user=self.user,
            client_type=APIApplication.CLIENT_CONFIDENTIAL,
            authorization_grant_type=APIApplication.GRANT_CLIENT_CREDENTIALS,
            name="machine client",
        )

        response = self.client.patch(f"{self.url}{machine.pk}/", {"name": "renamed"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        machine.refresh_from_db()
        self.assertEqual("machine client", machine.name)
        self.assertEqual(
            APIApplication.GRANT_CLIENT_CREDENTIALS, machine.authorization_grant_type
        )

    def test_delete_application(self):
        """Make sure permitted users can delete applications."""
        self.client.force_authenticate(self.user)
        Membership.objects.create(
            user=self.user,
            abakus_group=AbakusGroup.objects.get(name="APIApplicationTest"),
        )
        response = self.client.delete(
            "{base_url}{object_id}/".format(base_url=self.url, object_id=1)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
