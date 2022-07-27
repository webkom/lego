from rest_framework import status

from lego.apps.users.constants import GROUP_OTHER
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


class MembershipHistoryViewSetTestCase(BaseAPITestCase):

    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.url = "/api/v1/membership-history/"

    def test_list_without_auth(self):
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_list_history_as_admin(self):
        user = User.objects.get(username="test1")
        admin_group = AbakusGroup.objects.get(name="Webkom")
        group = AbakusGroup.objects.get(id=3)
        self.assertEqual(GROUP_OTHER, group.type)

        admin_group.add_user(user)
        group.add_user(user)
        group.remove_user(user)

        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.json()["results"]))

    def test_list_history_as_authenticated(self):
        user = User.objects.get(username="test1")
        group = AbakusGroup.objects.get(id=3)
        self.assertEqual(GROUP_OTHER, group.type)

        group.add_user(user)
        group.remove_user(user)

        self.client.force_authenticate(user)
        response = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.json()["results"]))
