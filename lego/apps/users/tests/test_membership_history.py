from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status

from lego.apps.users.constants import GROUP_OTHER
from lego.apps.users.models import AbakusGroup, MembershipHistory, User
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
        transaction.on_commit(
            lambda: self.assertEqual(1, len(response.json()["results"]))
        )

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

    def test_delete_history(self):
        user = User.objects.get(username="test1")
        group = AbakusGroup.objects.get(id=26)

        MembershipHistory.objects.create(
            user=user,
            abakus_group=group,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=2),
        )
        MembershipHistory.objects.create(
            user=user,
            abakus_group=group,
            start_date=timezone.now() + timedelta(days=4),
            end_date=timezone.now() + timedelta(days=6),
        )

        self.client.force_authenticate(user)
        url = f"/api/v1/membership-history/{group.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["result"], "AbaBrygg got deleted")
        self.assertFalse(
            MembershipHistory.objects.filter(user=user, abakus_group=group).exists()
        )

    def test_delete_history_empty_query(self):
        user = User.objects.get(username="test1")
        group = AbakusGroup.objects.get(id=26)

        MembershipHistory.objects.create(
            user=user,
            abakus_group=group,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=2),
        )
        MembershipHistory.objects.create(
            user=user,
            abakus_group=group,
            start_date=timezone.now() + timedelta(days=4),
            end_date=timezone.now() + timedelta(days=6),
        )

        self.client.force_authenticate(user)
        request_body = {"group_id": 0}
        response = self.client.delete(self.url, request_body)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue(
            MembershipHistory.objects.filter(user=user, abakus_group=group).exists()
        )

    def test_delete_history_no_group_history(self):
        user = User.objects.get(username="test1")
        group = AbakusGroup.objects.get(id=26)

        self.client.force_authenticate(user)
        request_body = {"group_id": 26}
        response = self.client.delete(self.url, request_body)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertFalse(
            MembershipHistory.objects.filter(user=user, abakus_group=group).exists()
        )
