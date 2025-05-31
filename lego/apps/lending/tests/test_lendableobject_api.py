from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from lego.apps.lending.constants import LENDING_REQUEST_STATUSES
from lego.apps.lending.models import LendableObject, LendingRequest
from lego.apps.lending.serializers import (
    LendableObjectAdminSerializer,
    LendableObjectSerializer,
)
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_list_url():
    return reverse("api:v1:lendable-object-list")


def get_detail_url(pk):
    return reverse("api:v1:lendable-object-detail", kwargs={"pk": pk})


def get_availability_url(pk, month, year):
    base_url = reverse("api:v1:lendable-object-availability", kwargs={"pk": pk})
    return f"{base_url}?month={month}&year={year}"


def create_user(username="testuser", **kwargs):
    return User.objects.create(
        username=username, email=username + "@abakus.no", **kwargs
    )


def create_lendable_object(**kwargs):
    return LendableObject.objects.create(
        title="Test objekt", description="Denne kan lånes!", **kwargs
    )


def create_lending_request(lendable_object, user, start_date, end_date, status=None):
    if status is None:
        status = LENDING_REQUEST_STATUSES["LENDING_APPROVED"]["value"]

    return LendingRequest.objects.create(
        lendable_object=lendable_object,
        created_by=user,
        start_date=start_date,
        end_date=end_date,
        status=status,
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
        self.permission_group.add_user(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lendable_object = response.json()["results"][0]
        self.assertEquals(
            len(LendableObjectSerializer.Meta.fields), len(lendable_object.keys())
        )


class RetrieveLendableObjectTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.lendable_object = create_lendable_object()

    def test_unauthenticated(self):
        response = self.client.get(get_detail_url(self.lendable_object.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_without_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.lendable_object.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_with_object_view_permissions(self):
        self.lendable_object.can_view_groups.add(self.group)
        self.lendable_object.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.lendable_object.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["canLend"], True)
        self.assertEqual(
            len(LendableObjectSerializer.Meta.fields + ("action_grant",)),
            len(response.json().keys()),
        )

    def test_authenticated_with_keyword_view_permissions(self):
        self.group.permissions = ["/sudo/admin/lendableobjects/view/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.lendable_object.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admins can see all lendable objects, but not necessarily lend them
        self.assertEqual(response.json()["canLend"], False)
        self.assertEqual(
            len(LendableObjectSerializer.Meta.fields + ("action_grant",)),
            len(response.json().keys()),
        )

    def test_admin_fields_keyword_permissions(self):
        self.group.permissions = [
            "/sudo/admin/lendableobjects/view/",
            "/sudo/admin/lendableobjects/edit/",
        ]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.lendable_object.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(LendableObjectAdminSerializer.Meta.fields + ("action_grant",)),
            len(response.json().keys()),
        )

    def test_admin_fields_object_permissions(self):
        self.lendable_object.can_view_groups.add(self.group)
        self.lendable_object.can_edit_groups.add(self.group)
        self.lendable_object.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_detail_url(self.lendable_object.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(LendableObjectAdminSerializer.Meta.fields + ("action_grant",)),
            len(response.json().keys()),
        )


class UpdateLendableObjectTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.lendable_object = create_lendable_object()

    def test_unauthenticated(self):
        response = self.client.patch(
            get_detail_url(self.lendable_object.pk), {"title": "New title"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_without_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.lendable_object.pk), {"title": "New title"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_with_object_edit_permissions(self):
        self.lendable_object.can_edit_groups.add(self.group)
        self.lendable_object.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.lendable_object.pk), {"title": "New title"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lendable_object.refresh_from_db()
        self.assertEqual(self.lendable_object.title, "New title")

    def test_authenticated_with_keyword_edit_permissions(self):
        self.group.permissions = ["/sudo/admin/lendableobjects/edit/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_detail_url(self.lendable_object.pk), {"title": "New title"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lendable_object.refresh_from_db()
        self.assertEqual(self.lendable_object.title, "New title")


class CreateLendableObjectTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)

    def test_unauthenticated(self):
        response = self.client.post(get_list_url(), {"title": "New title"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_without_permissions(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(get_list_url(), {"title": "New title"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_with_keyword_create_permissions(self):
        self.group.permissions = ["/sudo/admin/lendableobjects/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(get_list_url(), {"title": "New title"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        lendable_object = LendableObject.objects.get(title="New title")
        self.assertEqual(lendable_object.title, "New title")

    def test_authenticated_with_object_create_permissions(self):
        self.group.permissions = ["/sudo/admin/lendableobjects/create/"]
        self.group.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(get_list_url(), {"title": "New title"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        lendable_object = LendableObject.objects.get(title="New title")
        self.assertEqual(lendable_object.title, "New title")


class LendableObjectAvailabilityTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.group = create_group()
        self.group.add_user(self.user)
        self.lendable_object = create_lendable_object()

        self.now = timezone.now()
        self.year = self.now.year
        self.month = self.now.month

        self.start_of_month = timezone.make_aware(datetime(self.year, self.month, 1))

        self.borrower = create_user(username="borrower")

        self.lendable_object.can_view_groups.add(self.group)
        self.lendable_object.can_edit_groups.add(self.group)

        self.user.is_superuser = True
        self.user.save()

    def test_unauthenticated(self):
        url = get_availability_url(self.lendable_object.pk, self.month, self.year)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_without_permissions(self):
        # Create a regular user without permissions
        user_without_perms = create_user(username="nopermuser")
        self.client.force_authenticate(user=user_without_perms)

        url = get_availability_url(self.lendable_object.pk, self.month, self.year)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_month_parameter(self):
        self.client.force_authenticate(user=self.user)
        # Test with month=13 (invalid)
        url = get_availability_url(self.lendable_object.pk, 13, self.year)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"detail": "Month must be between 1 and 12."})

    def test_single_lending_request(self):
        self.client.force_authenticate(user=self.user)

        start_date = self.start_of_month
        end_date = start_date + timedelta(days=10)

        create_lending_request(
            lendable_object=self.lendable_object,
            user=self.borrower,
            start_date=start_date,
            end_date=end_date,
        )

        url = get_availability_url(self.lendable_object.pk, self.month, self.year)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

        unavailable_range = response.json()[0]
        self.assertEqual(len(unavailable_range), 2)
        self.assertEqual(unavailable_range[0], start_date.isoformat())
        self.assertEqual(unavailable_range[1], end_date.isoformat())

    def test_non_approved_request_not_included(self):
        self.client.force_authenticate(user=self.user)

        start_date = self.start_of_month
        end_date = start_date + timedelta(days=10)

        non_approved_status = LENDING_REQUEST_STATUSES["LENDING_DENIED"]["value"]

        create_lending_request(
            lendable_object=self.lendable_object,
            user=self.borrower,
            start_date=start_date,
            end_date=end_date,
            status=non_approved_status,
        )

        url = get_availability_url(self.lendable_object.pk, self.month, self.year)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])
