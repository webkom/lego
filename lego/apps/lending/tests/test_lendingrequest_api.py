from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status

from lego.apps.lending.models import LendableObject, LendingRequest
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_lending_request_list_url():
    return reverse("api:v1:lending-request-list")


def get_lending_request_detail_url(pk):
    return reverse("api:v1:lending-request-detail", kwargs={"pk": pk})


def create_user(username="testuser", **kwargs):
    return User.objects.create(
        username=username, email=f"{username}@abakus.no", **kwargs
    )


def create_lendable_object(**kwargs):
    return LendableObject.objects.create(
        title="Test Object", description="This is a test object", **kwargs
    )


def create_lending_request(user, lendable_object, **kwargs):
    return LendingRequest.objects.create(
        created_by=user,
        lendable_object=lendable_object,
        start_date=now() + timedelta(days=1),
        end_date=now() + timedelta(days=2),
        **kwargs,
    )


class LendingRequestTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = create_user()
        self.editor_user = create_user(username="editor_user")
        self.view_group = AbakusGroup.objects.create(name="view_group")
        self.edit_group = AbakusGroup.objects.create(name="edit_group")

        # Assign users to groups
        self.view_group.add_user(self.user)
        self.edit_group.add_user(self.editor_user)
        self.view_group.add_user(self.editor_user)

        self.lendable_object = create_lendable_object()
        self.lendable_object.can_view_groups.add(self.view_group)
        self.lendable_object.can_edit_groups.add(self.edit_group)

    def test_create_lending_request_with_permission(self):
        """Users in the can_view_groups should be able to create a lending request."""
        self.client.force_authenticate(user=self.user)

        data = {
            "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }

        response = self.client.post(get_lending_request_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LendingRequest.objects.count(), 1)

    def test_create_lending_request_without_permission(self):
        """Users not in can_view_groups should not be able to create a lending request."""
        other_user = create_user(username="other_user")
        self.client.force_authenticate(user=other_user)

        data = {
            "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }

        response = self.client.post(get_lending_request_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(LendingRequest.objects.count(), 0)

    def test_lending_request_validation(self):
        """Validate that serializer enforces start_date < end_date."""
        self.client.force_authenticate(user=self.user)

        data = {
            "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=2)).isoformat(),  # Invalid start_date
            "end_date": (now() + timedelta(days=1)).isoformat(),
        }

        response = self.client.post(get_lending_request_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("endDate", response.json())

    def test_user_edit_own_request(self):
        """Users should be able to edit their own requests by first creating it via the API."""
        # 1) Authenticate as self.user
        self.client.force_authenticate(user=self.user)

        # 2) Create the LendingRequest via the API, which should set created_by=self.user
        create_data = {
            "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        create_response = self.client.post(get_lending_request_list_url(), create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Extract the new LendingRequest's id
        created_request_id = create_response.json()["id"]

        # 3) Attempt to edit (patch) the lending request we just created
        patch_data = {
            "end_date": (now() + timedelta(days=3)).isoformat(),
        }
        patch_response = self.client.patch(
            get_lending_request_detail_url(created_request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Optionally, check that the change stuck (and that created_by is set properly)
        lending_request = LendingRequest.objects.get(pk=created_request_id)
        self.assertEqual(lending_request.end_date.isoformat(), patch_data["end_date"])
        self.assertEqual(lending_request.created_by, self.user)

    def test_user_with_edit_permission_can_approve_request(self):
        """Users in can_edit_groups should be able to approve lending requests."""
        lending_request = create_lending_request(self.user, self.lendable_object)

        self.client.force_authenticate(user=self.editor_user)

        data = {"status": "approved"}
        response = self.client.patch(
            get_lending_request_detail_url(lending_request.pk), data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lending_request.refresh_from_db()
        self.assertEqual(lending_request.status, "approved")

    def test_user_without_edit_permission_cannot_approve_request(self):
        """Users not in can_edit_groups should not be able to approve lending requests."""
        lending_request = create_lending_request(self.user, self.lendable_object)

        other_user = create_user(username="other_user")
        self.client.force_authenticate(user=other_user)

        data = {"status": "approved"}
        response = self.client.patch(
            get_lending_request_detail_url(lending_request.pk), data
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        lending_request.refresh_from_db()
        self.assertEqual(lending_request.status, "unapproved")

    def test_user_without_edit_permission_but_view_permission_cannot_approve_request(
        self,
    ):
        """Users not in edit but in view cannot approve."""
        lending_request = create_lending_request(self.user, self.lendable_object)

        other_user = create_user(username="other_user")
        self.view_group.add_user(other_user)
        self.client.force_authenticate(user=other_user)

        data = {"status": "approved"}
        response = self.client.patch(
            get_lending_request_detail_url(lending_request.pk), data
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        lending_request.refresh_from_db()
        self.assertEqual(lending_request.status, "unapproved")


class LendingRequestStatusTestCase(BaseAPITestCase):
    def setUp(self):
        # Create users
        self.user_view_only = User.objects.create(
            username="view_user", email="mail2@abakus.no"
        )
        self.user_edit = User.objects.create(
            username="edit_user", email="mail@abakus.no"
        )

        # Create groups
        self.view_group = AbakusGroup.objects.create(name="view_group")
        self.edit_group = AbakusGroup.objects.create(name="edit_group")

        # Assign users to groups
        self.view_group.add_user(self.user_view_only)
        self.view_group.add_user(self.user_edit)
        self.edit_group.add_user(self.user_edit)

        # Create a LendableObject and give view permission to the view_group,
        # and edit permission to the edit_group
        self.lendable_object = self._create_lendable_object()
        self.lendable_object.can_view_groups.add(self.view_group)
        self.lendable_object.can_edit_groups.add(self.edit_group)

    def _create_lendable_object(self):
        # Utility method to keep code clear
        from lego.apps.lending.models import LendableObject

        return LendableObject.objects.create(
            title="Test Object", description="Test Description"
        )

    #
    # CREATE TESTS
    #
    def test_create_lending_request_must_be_unapproved_if_status_provided(self):
        """
        On create, the status must be 'unapproved'.
        If another status is given, expect a 400 ValidationError.
        """
        self.client.force_authenticate(user=self.user_view_only)
        invalid_data = {
            "lendable_object": self.lendable_object.pk,
            "status": "approved",  # Not allowed on create
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(get_lending_request_list_url(), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_create_lending_request_defaults_to_unapproved(self):
        """
        If 'status' is not provided (or is None) on create,
        it should default to 'unapproved' and succeed.
        """
        self.client.force_authenticate(user=self.user_view_only)
        data = {
            "lendable_object": self.lendable_object.pk,
            # No 'status' key
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(get_lending_request_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        request_id = response.data["id"]
        lending_request = LendingRequest.objects.get(id=request_id)
        self.assertEqual(lending_request.status, "unapproved")

    def test_create_lending_request_with_status_unapproved_is_ok(self):
        """
        If the user explicitly sets 'unapproved' on create, that's allowed.
        """
        self.client.force_authenticate(user=self.user_view_only)
        data = {
            "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        response = self.client.post(get_lending_request_list_url(), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        request_id = response.data["id"]
        lending_request = LendingRequest.objects.get(id=request_id)
        self.assertEqual(lending_request.status, "unapproved")

    #
    # UPDATE TESTS
    #
    def test_update_status_by_non_edit_user_can_only_be_cancelled_or_unapproved(self):
        """
        A user without edit permission (only in view group) can only set status
        to 'cancelled' or 'unapproved'.
        """
        # 1) Create a request as user_view_only
        self.client.force_authenticate(user=self.user_view_only)
        create_data = {
            "lendable_object": self.lendable_object.pk,
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        create_response = self.client.post(get_lending_request_list_url(), create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        request_id = create_response.data["id"]

        # 2) Try to update the status to "approved" which is not allowed for non-edit user
        patch_data = {"status": "approved"}
        patch_response = self.client.patch(
            get_lending_request_detail_url(request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", patch_response.data)

        # 3) Update it to "cancelled" -> should succeed
        patch_data = {"status": "cancelled"}
        patch_response = self.client.patch(
            get_lending_request_detail_url(request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Confirm it's updated
        lending_request = LendingRequest.objects.get(id=request_id)
        self.assertEqual(lending_request.status, "cancelled")

    def test_update_status_by_edit_user_to_approved_is_ok(self):
        """
        A user with edit permission can set status to 'approved' (or any valid status).
        """
        # 1) Create the request as a normal (view-only) user
        self.client.force_authenticate(user=self.user_view_only)
        create_data = {
            "lendable_object": self.lendable_object.pk,
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        create_response = self.client.post(get_lending_request_list_url(), create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        request_id = create_response.data["id"]

        # 2) Now authenticate as the edit user and approve the request
        self.client.force_authenticate(user=self.user_edit)
        patch_data = {"status": "approved"}
        patch_response = self.client.patch(
            get_lending_request_detail_url(request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Confirm it's updated
        lending_request = LendingRequest.objects.get(id=request_id)
        self.assertEqual(lending_request.status, "approved")
