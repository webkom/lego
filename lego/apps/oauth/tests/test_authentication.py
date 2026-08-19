from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from oauth2_provider.models import AccessToken

from lego.apps.oauth.models import APIApplication
from lego.apps.users.models import User
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
