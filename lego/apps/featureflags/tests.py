from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.featureflags.models import FeatureFlag
from lego.apps.users.models import AbakusGroup

User = get_user_model()


def get_admin_featureflag_list_url():
    return reverse("api:v1:featureflagadmin-list")


def get_admin_featureflag_detail_url(pk):
    return reverse("api:v1:featureflagadmin-detail", kwargs={"pk": pk})


def get_public_featureflag_list_url():
    return reverse("api:v1:featureflag-list")


def get_public_featureflag_detail_url(identifier):
    return reverse("api:v1:featureflag-detail", kwargs={"identifier": identifier})


class FeatureFlagAPITestCase(APITestCase):
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        self.user = User.objects.create(
            username="testuser", password="pass", email="someemail@mail.net"
        )
        self.admin_group = AbakusGroup.objects.get(name="Webkom")
        self.feature_flag_data = {
            "identifier": "test-feature",
            "is_active": True,
            "percentage": 50,
            "display_groups": [],
        }

    def test_create_feature_flag_without_permission(self):
        """
        Ensure a normal user cannot create a feature flag.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            get_admin_featureflag_list_url(), self.feature_flag_data, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="A user without admin permissions should be forbidd from creating.",
        )

    def test_create_feature_flag_with_permission(self):
        """
        Ensure an admin user can create a feature flag.
        """
        self.admin_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            get_admin_featureflag_list_url(), self.feature_flag_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["identifier"], "test-feature")

    def test_retrieve_public_feature_flag(self):
        """
        Ensure public users can retrieve a feature flag.
        """
        FeatureFlag.objects.create(identifier="test-feature", is_active=True)
        response = self.client.get(get_public_featureflag_detail_url("test-feature"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["identifier"], "test-feature")

    def test_retrieve_admin_feature_flag_without_permission(self):
        """
        Ensure a normal user cannot access an admin feature flag.
        """
        FeatureFlag.objects.create(identifier="test-feature", is_active=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_admin_featureflag_detail_url("test-feature"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_admin_feature_flag_with_permission(self):
        """
        Ensure an admin can retrieve a feature flag.
        """
        flag = FeatureFlag.objects.create(identifier="test-feature", is_active=True)
        self.admin_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(get_admin_featureflag_detail_url(flag.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_feature_flag_without_permission(self):
        """
        Ensure a normal user cannot update a feature flag.
        """
        feature_flag = FeatureFlag.objects.create(
            identifier="test-feature", is_active=True
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_admin_featureflag_detail_url(feature_flag.identifier),
            {"isActive": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_feature_flag_with_permission(self):
        """
        Ensure an admin user can update a feature flag.
        """
        feature_flag = FeatureFlag.objects.create(
            identifier="test-feature", is_active=True
        )
        self.admin_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            get_admin_featureflag_detail_url(feature_flag.id),
            {"isActive": False},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json()["isActive"])

    def test_delete_feature_flag_without_permission(self):
        """
        Ensure a normal user cannot delete a feature flag.
        """
        feature_flag = FeatureFlag.objects.create(
            identifier="test-feature", is_active=True
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_admin_featureflag_detail_url(feature_flag.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_feature_flag_with_permission(self):
        """
        Ensure an admin user can delete a feature flag.
        """
        feature_flag = FeatureFlag.objects.create(
            identifier="test-feature", is_active=True
        )
        self.admin_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(get_admin_featureflag_detail_url(feature_flag.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_percentage_validator_api(self):
        """
        Ensure percentage validator works correctly via the API.
        """
        self.admin_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)

        # Attempt to create a feature flag with invalid percentage (above 100)
        response = self.client.post(
            get_admin_featureflag_list_url(),
            {
                "identifier": "test-feature",
                "is_active": True,
                "percentage": 105,
                "allowed_identifier": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.json())

        # Attempt to create a feature flag with invalid percentage (below -100)
        response = self.client.post(
            get_admin_featureflag_list_url(),
            {
                "identifier": "test-feature-2",
                "is_active": True,
                "percentage": -101,
                "allowed_identifier": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.json())

        # Create a feature flag with a valid percentage
        response = self.client.post(
            get_admin_featureflag_list_url(),
            {
                "identifier": "test-feature-valid",
                "is_active": True,
                "percentage": 50,
                "allowed_identifier": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_webkom_user_cannot_access_inactive_feature_flag(self):
        """
        Ensure that even an admin user in Webkom cannot access.
        """
        FeatureFlag.objects.create(
            identifier="inactive-feature",
            is_active=False,
        )

        # Add user to Webkom admin group
        self.admin_group.add_user(self.user)
        self.client.force_authenticate(user=self.user)

        # Attempt to retrieve the feature flag
        response = self.client.get(
            get_public_featureflag_detail_url("inactive-feature")
        )

        # Ensure the feature flag is not accessible
        self.assertEqual(response.json()["canSeeFlag"], False)


class FeatureFlagAlgorithmTestCase(TestCase):
    def test_deterministic_selection_with_precomputed_values(self):
        """
        Test that the deterministic selection algorithm produces expected results
        for a set of precomputed user IDs and percentages.
        """

        # Precomputed expected results for (user_id, percentage)
        # These are manually checked results to ensure consistency.
        precomputed_results = [
            (1, False),
            (2, True),
            (3, False),
            (4, False),
            (5, True),
            (6, False),
            (7, True),
            (8, True),
            (9, False),
            (10, True),
        ]

        for user_id, expected in precomputed_results:
            with self.subTest(user_id=user_id):
                percentage = 50
                result = FeatureFlag._deterministic_selection(user_id, percentage)
                self.assertEqual(
                    result,
                    expected,
                    "Failed",
                )
