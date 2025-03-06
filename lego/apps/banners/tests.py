from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.banners.models import Banners

User = get_user_model()


def get_banner_list_url():
    return reverse("api:v1:banner-list")


def get_banner_detail_url(pk):
    return reverse("api:v1:banner-detail", kwargs={"pk": pk})


def get_current_public_url():
    return reverse("api:v1:banner-current-public")


def get_current_private_url():
    return reverse("api:v1:banner-current-private")


class BannersPermissionTestCase(APITestCase):
    # Import the fixture containing the Abakus groups.
    fixtures = ["test_abakus_groups.yaml"]

    def setUp(self):
        # Create a test user.
        self.user = User.objects.create_user(username="testuser", password="pass")
        # Get the admin group from the fixture (adjust the group name if needed).
        from lego.apps.users.models import AbakusGroup

        self.admin_group = AbakusGroup.objects.get(name="Webkom")
        self.default_data = {
            "header": "Test Banner",
            "subheader": "Test Subheader",
            "link": "http://example.com",
            "color": "red",  # assuming "red" is a valid option
            "current_public": False,
            "current_private": False,
        }

    def test_banner_create_without_permission(self):
        """
        Users not in the admin group should not be able to create a banner.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            get_banner_list_url(), self.default_data, format="json"
        )
        # Expect forbidden if the user lacks proper permission.
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="A user without admin group membership should be forbidden from creating a banner.",
        )

    def test_banner_create_with_permission(self):
        """
        A user added to the admin group should be able to create a banner.
        """
        self.client.force_authenticate(user=self.user)
        # Grant banner creation permission by adding the user to the admin group.
        self.admin_group.add_user(self.user)
        response = self.client.post(
            get_banner_list_url(), self.default_data, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg="A user in the admin group should be able to create a banner.",
        )

    def test_current_private_endpoint_requires_authentication(self):
        """
        The current_private endpoint requires authentication.
        An unauthenticated request should return a 401 Unauthorized.
        """
        # Without authentication.
        response = self.client.get(get_current_private_url())
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg="The current_private endpoint should require authentication.",
        )

    def test_current_public_endpoint_allows_anonymous(self):
        """
        The current_public endpoint uses AllowAny and should permit anonymous access.
        If a banner exists, it should return the banner; if not, a 204.
        """
        # First, authenticate and create a banner with current_public True.
        self.client.force_authenticate(user=self.user)
        self.admin_group.add_user(self.user)
        data = self.default_data.copy()
        data["current_public"] = True
        response = self.client.post(get_banner_list_url(), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        banner = response.json()

        # Now, remove authentication to simulate an anonymous request.
        self.client.force_authenticate(user=None)
        response = self.client.get(get_current_public_url())
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg="The current_public endpoint should allow anonymous access when a banner exists.",
        )
        data = response.json()
        self.assertEqual(
            data["id"],
            banner["id"],
            msg="The current_public endpoint should return the correct banner.",
        )
        self.assertTrue(data["currentPublic"])

    def test_current_public_endpoint_returns_204_if_none(self):
        """
        When no banner is marked as current_public, the endpoint should return a 204.
        """
        # Ensure no banner has current_public True.
        Banners.objects.all().update(current_public=False)
        self.client.force_authenticate(user=None)
        response = self.client.get(get_current_public_url())
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            msg="The current_public endpoint should return 204 if no banner is marked as current_public.",
        )
