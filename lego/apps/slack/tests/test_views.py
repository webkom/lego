from unittest import mock

from rest_framework import status

from lego.apps.slack.utils import SlackException
from lego.apps.users.models import User
from lego.utils.test_utils import BaseAPITestCase


class SlackInviteTestCase(BaseAPITestCase):

    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.url = "/api/v1/slack-invite/"

    def test_invite_no_auth(self):
        response = self.client.post(self.url, {"email": "test@test.com"})
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch(
        "lego.apps.slack.utils.SlackInvite._post",
        side_effect=SlackException("test_error"),
    )
    def test_invite_user(self, mock_post):
        user = User.objects.first()
        self.client.force_login(user)
        response = self.client.post(self.url, {"email": "test@test.com"})
        self.assertEquals(response.json(), {"detail": "test_error"})
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
