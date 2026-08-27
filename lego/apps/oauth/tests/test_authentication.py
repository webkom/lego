from datetime import timedelta
from urllib.parse import urlencode

from django.utils import timezone
from rest_framework import status

from oauth2_provider.models import AccessToken

from lego.apps.oauth.models import APIApplication
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


class UserScopeAuthenticationTestCase(BaseAPITestCase):
    """A `user`-scoped token reaches an explicit allowlist and nothing else."""

    fixtures = ["test_users.yaml", "test_applications.yaml"]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.application = APIApplication.objects.first()

    def _token(self, scope):
        token = AccessToken.objects.create(
            application=self.application,
            user=self.user,
            token=f"token-{scope.replace(' ', '-')}",
            scope=scope,
            expires=timezone.now() + timedelta(days=1),
        )
        return f"Bearer {token.token}"

    def test_user_scope_reaches_autocomplete(self):
        """Applications such as admissions let a signed-in member look someone
        up by name; without this they would have to hold an `all` token."""
        response = self.client.post(
            "/api/v1/search-autocomplete/",
            {"query": "test", "types": ["users.user"]},
            HTTP_AUTHORIZATION=self._token("user"),
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_user_scope_is_still_refused_elsewhere(self):
        """The allowlist must stay an allowlist."""
        response = self.client.get(
            "/api/v1/users/",
            HTTP_AUTHORIZATION=self._token("user"),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_all_scope_is_unaffected(self):
        response = self.client.get(
            "/api/v1/users/",
            HTTP_AUTHORIZATION=self._token("all"),
        )

        self.assertNotEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)


class ClientCredentialsAuthenticationTestCase(BaseAPITestCase):
    """A user-less (client_credentials) token acts as the application's
    owner, whose permissions are the credential's ceiling."""

    fixtures = ["test_users.yaml", "test_applications.yaml"]

    def setUp(self):
        self.owner = User.objects.get(id=1)

    def _machine_application(self, **overrides):
        fields = {
            "user": self.owner,
            "client_type": APIApplication.CLIENT_CONFIDENTIAL,
            "authorization_grant_type": APIApplication.GRANT_CLIENT_CREDENTIALS,
            "name": "machine client",
        }
        fields.update(overrides)
        return APIApplication.objects.create(**fields)

    def _machine_token(self, application, token="machine-token"):
        access_token = AccessToken.objects.create(
            application=application,
            user=None,
            token=token,
            scope="all",
            expires=timezone.now() + timedelta(days=1),
        )
        return f"Bearer {access_token.token}"

    def test_machine_token_acts_as_application_owner(self):
        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(self._machine_application()),
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.owner.username, response.json()["username"])

    def test_machine_token_is_refused_when_application_has_no_owner(self):
        ownerless = self._machine_application(user=None, name="ownerless machine")

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(ownerless),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_machine_token_is_refused_when_owner_is_deactivated(self):
        application = self._machine_application()
        self.owner.is_active = False
        self.owner.save()

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(application),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_machine_token_is_refused_when_owner_is_soft_deleted(self):
        """The soft delete leaves is_active=True; `deleted` has its own check."""
        application = self._machine_application()
        self.owner.delete()

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(application),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_user_less_token_is_refused_for_non_machine_applications(self):
        password_app = APIApplication.objects.get(pk=1)

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(password_app),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_user_less_token_is_refused_for_confidential_password_application(self):
        """Pins the grant-type half of the guard on its own."""
        application = self._machine_application(
            authorization_grant_type=APIApplication.GRANT_PASSWORD,
        )

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(application),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_user_less_token_is_refused_for_public_client_credentials_application(self):
        """Pins the client-type half of the guard on its own."""
        application = self._machine_application(
            client_type=APIApplication.CLIENT_PUBLIC,
        )

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=self._machine_token(application),
        )

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_machine_token_flows_through_the_owner_permission_stack(self):
        """A keyword permission granted to the owner works through a machine
        token on a real endpoint - and is refused without it."""
        token = self._machine_token(self._machine_application())
        target = AbakusGroup.objects.create(name="Roster target")

        response = self.client.get(
            f"/api/v1/groups/{target.pk}/memberships/",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        sync_group = AbakusGroup.objects.create(
            name="Roster sync",
            permissions=["/sudo/admin/groups/list/"],
        )
        sync_group.add_user(self.owner)

        response = self.client.get(
            f"/api/v1/groups/{target.pk}/memberships/",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_client_credentials_grant_round_trip(self):
        """The exact flow a machine client performs."""
        secret = "machine-secret"
        application = self._machine_application(client_secret=secret)

        token_response = self.client.post(
            "/authorization/oauth2/token/",
            urlencode(
                {
                    "grant_type": "client_credentials",
                    "client_id": application.client_id,
                    "client_secret": secret,
                }
            ),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(
            status.HTTP_200_OK, token_response.status_code, token_response.content
        )
        access_token = token_response.json()["access_token"]

        response = self.client.get(
            "/api/v1/users/oauth2_userdata/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.owner.username, response.json()["username"])
