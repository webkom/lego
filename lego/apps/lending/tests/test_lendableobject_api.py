from django.urls import reverse
from rest_framework import status

from lego.apps.lending.models import LendableObject
from lego.apps.lending.serializers import LendableObjectSerializer
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_list_url():
    return reverse("api:v1:lendable-object-list")


def get_detail_url(pk):
    return reverse("api:v1:lendable-object-detail", kwargs={"pk": pk})


def create_user(username="testuser", **kwargs):
    return User.objects.create(
        username=username, email=username + "@abakus.no", **kwargs
    )


def create_lendable_object(**kwargs):
    return LendableObject.objects.create(
        title="Test objekt", description="Denne kan lånes!", **kwargs
    )


group_name_suffix = 1


def create_group(**kwargs):
    global group_name_suffix
    group = AbakusGroup.objects.create(
        name="group_{}".format(group_name_suffix), **kwargs
    )
    group_name_suffix += 1
    return group


class ListLendableObjectsTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.permission_group = create_group()

        self.lendable_object = create_lendable_object()

        self.object_permission_lendable_object = create_lendable_object()
        self.object_permission_lendable_object.can_view_groups.add(
            self.permission_group
        )

    def test_unauthenticated_user(self):
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)

    def test_with_keyword_permissions(self):
        # Admins should be able to see all lendable objects
        self.group.permissions = ["/sudo/admin/lendableobjects/list/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 2)

    def test_with_object_permissions(self):
        self.permission_group.add_user(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)

    def test_fields(self):
        self.lendable_object.can_view_groups.add(self.group)
        self.lendable_object.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lendable_object = response.json()["results"][0]
        self.assertListEqual(
            list(LendableObjectSerializer.Meta.fields), list(lendable_object.keys())
        )
