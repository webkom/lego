from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status

from lego.apps.lending.constants import (
    LENDING_REQUEST_STATUSES,
    LENDING_REQUEST_TRANSLATION_MAP,
)
from lego.apps.lending.models import LendableObject, LendingRequest
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def get_lending_request_list_url():
    return reverse("api:v1:lending-request-list")


def get_lending_request_timelineentry_url():
    return reverse("api:v1:lending-timelineentry-list")


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

    def test_set_changes_resolved_without_changes_requested(self):
        """Users should be unable to set status to changes resolved if changes are not requested"""
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

        patch_data = {
            "status": "changes_resolved",
        }
        patch_response = self.client.patch(
            get_lending_request_detail_url(response.json()["id"]), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_edit_own_request_and_comment(self):
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

        timeline_data = {"lending_request": created_request_id, "message": "Hei"}
        response2 = self.client.post(
            get_lending_request_timelineentry_url(), timeline_data
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_user_with_edit_permission_can_approve_request_and_comment(self):
        """Users in can_edit_groups should be able to approve lending requests."""
        self.client.force_authenticate(user=self.user)

        data = {
            "lendable_object": self.lendable_object.pk,
            "status": "unapproved",
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }

        response1 = self.client.post(get_lending_request_list_url(), data)
        lending_request = LendingRequest.objects.get(pk=response1.data["id"])
        self.client.force_authenticate(user=self.editor_user)

        data = {"status": "approved"}
        response = self.client.patch(
            get_lending_request_detail_url(lending_request.pk), data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lending_request.refresh_from_db()
        self.assertEqual(lending_request.status, "approved")

        timeline_data = {"lending_request": lending_request.id, "message": "Hei"}
        response2 = self.client.post(
            get_lending_request_timelineentry_url(), timeline_data
        )
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_user_without_edit_permission_cannot_approve_request_or_comment(self):
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
        timeline_data = {"lending_request": lending_request.id, "message": "Hei"}
        response2 = self.client.post(
            get_lending_request_timelineentry_url(), timeline_data
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_admin_endpoint_returns_only_requests_for_editable_objects(self):
        """
        The /admin endpoint should return only lending requests where the requesting user has
        edit permission on the associated lendable object.
        """
        # Create another lendable object without granting edit permissions to self.editor_user.
        other_object = LendableObject.objects.create(
            title="Other object",
            description="Other object",
        )
        # For other_object, only add view permissions.
        other_object.can_view_groups.add(self.view_group)
        # Note: self.lendable_object already grants edit access to
        # self.editor_user via self.edit_group.

        # Create two lending requests by self.editor_user:
        # 1. For the object where the user has edit permission.
        request_editable = create_lending_request(
            self.editor_user, self.lendable_object
        )
        # 2. For the object where the user does NOT have edit permission.
        request_non_editable = create_lending_request(self.editor_user, other_object)

        # Authenticate as the editor user and access the /admin endpoint.
        self.client.force_authenticate(user=self.editor_user)
        response = self.client.get(reverse("api:v1:lending-request-admin"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        returned_ids = [req["id"] for req in data["results"]]
        # Check that only the request associated with the object they can edit appears.
        self.assertIn(request_editable.id, returned_ids)
        self.assertNotIn(request_non_editable.id, returned_ids)

    def test_filter_by_status(self):
        """Test filtering lending requests by status - both single and multiple status filters."""
        # Create multiple lending requests with different statuses
        # All created by self.user to ensure they appear in the list endpoint
        request1 = create_lending_request(
            user=self.user, lendable_object=self.lendable_object, status="unapproved"
        )
        request2 = create_lending_request(
            user=self.user, lendable_object=self.lendable_object, status="approved"
        )
        request3 = create_lending_request(
            user=self.user, lendable_object=self.lendable_object, status="cancelled"
        )

        self.client.force_authenticate(user=self.editor_user)

        # Test no filter
        response = self.client.get(reverse("api:v1:lending-request-admin"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["id"], request1.id)
        self.assertEqual(results[1]["id"], request2.id)
        self.assertEqual(results[2]["id"], request3.id)

        # Test single status filter
        response = self.client.get(
            f"{reverse('api:v1:lending-request-admin')}?status=approved"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], request2.id)

        # Test multiple status filter
        response = self.client.get(
            f"{reverse('api:v1:lending-request-admin')}?status=approved,cancelled"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], request2.id)
        self.assertEqual(results[1]["id"], request3.id)


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


class LendingRequestAdditionalPermissionTestCase(BaseAPITestCase):
    def setUp(self):
        # Create two users:
        # creator_user will create the request
        # other_user will attempt to update someone else's request.
        self.creator_user = User.objects.create(
            username="creator_user", email="creator@abakus.no"
        )
        self.other_user = User.objects.create(
            username="other_user", email="other@abakus.no"
        )

        # Create groups for permissions (if needed)
        self.view_group = AbakusGroup.objects.create(name="view_group")
        self.edit_group = AbakusGroup.objects.create(name="edit_group")
        self.view_group.add_user(self.creator_user)
        self.view_group.add_user(self.other_user)
        # Let’s assume edit permission is granted only to creator_user for this test.
        self.edit_group.add_user(self.creator_user)

        # Create a lendable object and assign permissions.
        from lego.apps.lending.models import LendableObject

        self.lendable_object = LendableObject.objects.create(
            title="Test Object", description="Testing object"
        )
        self.lendable_object.can_view_groups.add(self.view_group)
        self.lendable_object.can_edit_groups.add(self.edit_group)

        # Create a lending request as the creator.
        self.client.force_authenticate(user=self.creator_user)
        create_data = {
            "lendable_object": self.lendable_object.pk,
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
            # Optionally add a text field here.
        }
        response = self.client.post(get_lending_request_list_url(), create_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.request_id = response.data["id"]

    def test_non_creator_cannot_cancel_request(self):
        """
        Verify that a user who did not create the lending request
        cannot update its status to 'cancelled'.
        """
        # Attempt to cancel the lending request as other_user.
        self.client.force_authenticate(user=self.other_user)
        self.edit_group.add_user(self.other_user)
        patch_data = {"status": LENDING_REQUEST_STATUSES["LENDING_CANCELLED"]["value"]}
        patch_response = self.client.patch(
            get_lending_request_detail_url(self.request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", patch_response.data)
        self.assertIn(
            "You cannot cancel someone else's request", patch_response.data["status"][0]
        )

    def test_non_creator_cannot_update_text(self):
        """
        Verify that a user who did not create the lending request
        cannot update its text field.
        """
        # Attempt to update the text as other_user.
        self.edit_group.add_user(self.other_user)
        self.client.force_authenticate(user=self.other_user)
        patch_data = {"text": "Attempted update by non-creator."}
        patch_response = self.client.patch(
            get_lending_request_detail_url(self.request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", patch_response.data)
        self.assertIn(
            "You cannot edit someone else's request", patch_response.data["text"][0]
        )

    def test_creation_creates_system_linelineentry(self):
        """
        Verify that when a lending request is created, a system message
        timelineentry is created reflecting the creation.
        """
        # Reload the request from the database.
        updated_request = LendingRequest.objects.get(pk=self.request_id)
        # Check that a timelineentry was created for the creation.
        self.assertTrue(updated_request.timeline_entries.exists())

        # Verify the timelineentry text matches the expected system message.
        # Expected text: "opprettet forespørsel"
        expected_text = LENDING_REQUEST_TRANSLATION_MAP["created"]
        system_timelineentry = updated_request.timeline_entries.order_by(
            "created_at"
        ).first()
        self.assertEqual(system_timelineentry.message, expected_text)

    def test_creator_update_status_creates_system_timelineentry(self):
        """
        Verify that when the creator updates the status of their own request,
        a system message timelineentry is created reflecting the status change.
        """
        # Update the status as the creator.
        self.client.force_authenticate(user=self.creator_user)
        patch_data = {"status": "approved"}
        patch_response = self.client.patch(
            get_lending_request_detail_url(self.request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Reload the request from the database.
        updated_request = LendingRequest.objects.get(pk=self.request_id)
        # Check that a timelineentry was created for the status update.
        self.assertTrue(updated_request.timeline_entries.exists())

        # Verify the timelineentry text matches the expected system message.
        # Expected text: "Status endret fra {translated old status} til {translated new status}."
        expected_text = LENDING_REQUEST_TRANSLATION_MAP["approved"]
        system_timelineentry = updated_request.timeline_entries.order_by(
            "created_at"
        ).last()
        self.assertEqual(system_timelineentry.message, expected_text)


class LendingRequestApprovalByDifferentUserTestCase(BaseAPITestCase):
    def setUp(self):
        # Create a creator user and an approver user.
        self.creator_user = User.objects.create(
            username="creator", email="creator@example.com"
        )
        self.approver_user = User.objects.create(
            username="approver", email="approver@example.com"
        )

        # Create permission groups.
        self.view_group = AbakusGroup.objects.create(name="view_group")
        self.edit_group = AbakusGroup.objects.create(name="edit_group")

        # Assign permissions:
        #   - The creator is only in the view group.
        #   - The approver is in both view and edit groups.
        self.view_group.add_user(self.creator_user)
        self.view_group.add_user(self.approver_user)
        self.edit_group.add_user(self.approver_user)

        # Create a lendable object and assign the groups.
        self.lendable_object = LendableObject.objects.create(
            title="Test Object", description="Testing object"
        )
        self.lendable_object.can_view_groups.add(self.view_group)
        self.lendable_object.can_edit_groups.add(self.edit_group)

    def test_different_user_approves_request_creates_system_timelineentry(self):
        # Step 1: Creator creates the
        # lending request (status defaults to "unapproved").
        self.client.force_authenticate(user=self.creator_user)
        create_data = {
            "lendable_object": self.lendable_object.pk,
            "start_date": (now() + timedelta(days=1)).isoformat(),
            "end_date": (now() + timedelta(days=2)).isoformat(),
        }
        create_response = self.client.post(get_lending_request_list_url(), create_data)
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        request_id = create_response.data["id"]

        # Step 2: Approver (a different user)
        #  updates the request's status to "approved".
        self.client.force_authenticate(user=self.approver_user)
        patch_data = {"status": "approved"}
        patch_response = self.client.patch(
            get_lending_request_detail_url(request_id), patch_data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        # Step 3: Verify that the lending request now has
        # a system timelineentry reflecting the status change.
        updated_request = LendingRequest.objects.get(pk=request_id)
        self.assertTrue(
            updated_request.timeline_entries.exists(), "Expected timelineentry."
        )

        expected_text = LENDING_REQUEST_TRANSLATION_MAP["approved"]
        system_timelineentry = updated_request.timeline_entries.order_by(
            "created_at"
        ).last()
        self.assertEqual(system_timelineentry.message, expected_text)
        self.assertEqual(system_timelineentry.is_system, True)
        # Optionally check that the entry was created by the approver.
        self.assertEqual(system_timelineentry.created_by, self.approver_user)
