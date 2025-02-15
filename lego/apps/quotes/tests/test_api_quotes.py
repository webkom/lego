from django.urls import reverse
from rest_framework import status

from lego.apps.quotes.models import Quote
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_list_url():
    return reverse("api:v1:quote-list")


def _get_list_approved_url():
    return _get_list_url() + "?approved=True"


def _get_list_unapproved_url():
    return _get_list_url() + "?approved=False"


def _get_detail_url(pk):
    return reverse("api:v1:quote-detail", kwargs={"pk": pk})


def _get_approve_url(pk):
    return reverse("api:v1:quote-approve", kwargs={"pk": pk})


def _get_unapprove_url(pk):
    return reverse("api:v1:quote-unapprove", kwargs={"pk": pk})


class QuoteViewSetTestCase(BaseAPITestCase):
    fixtures = ["test_users.yaml", "test_abakus_groups.yaml", "test_quotes.yaml"]

    def setUp(self):
        self.authenticated_user = User.objects.get(username="test1")
        self.group = AbakusGroup.objects_with_text.get(name="QuoteAdminTest")
        self.group.add_user(self.authenticated_user)
        self.unauthenticated_user = User.objects.get(username="test2")

        self.quote_data = {"text": "TestText", "source": "TestSource"}

    def test_create_authenticated(self):
        """Users with permissions should be able to create quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.post(_get_list_url(), self.quote_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_unauthenticated(self):
        """Users with no permissions should not be able to create quotes"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.post(_get_list_url(), self.quote_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_authenticated(self):
        """Users with permissions should be able to list quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_list_approved_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_list_unauthenticated(self):
        """Users with no permissions should not be able to list quotes"""
        self.client.force_authenticate(user=self.unauthenticated_user)
        response = self.client.get(_get_list_approved_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_authenticated(self):
        """Users with permissions should be able to see detailed quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_detail_unauthenticated(self):
        """Users with no permissions should not be able see detailed quotes"""
        self.client.force_authenticate(user=self.unauthenticated_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_authenticated(self):
        """Users with permissions should be able to approve quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.put(_get_approve_url(3))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        quote = Quote.objects.get(id=3)
        self.assertTrue(quote.approved)

    def test_approve_permission(self):
        """Users should not have permission to approve their own quotes"""
        self.client.force_authenticate(self.authenticated_user)
        self.client.post(_get_list_url(), self.quote_data)
        response = self.client.put(_get_approve_url(4))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        quote = Quote.objects.get(id=4)
        self.assertFalse(quote.approved)

    def test_approve_unauthenticated(self):
        """Users with no permissions should not be able to approve quotes"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.put(_get_approve_url(3))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_unapproved_authenticated(self):
        """Users with permissions should be able to see unapproved quotes"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_list_unapproved_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_quote = response.json()["results"][0]
        self.assertFalse(first_quote["approved"])

    def test_list_unapproved_unauthenticated(self):
        """Users with no permissions should not be able to see unapproved quotes"""
        self.client.force_authenticate(self.unauthenticated_user)

        response = self.client.get(_get_list_unapproved_url())
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_list_approved_unauthorized(self):
        """Users with regular permissions should be able to see approved quotes"""
        self.group.permissions.remove("/sudo/admin/quotes/edit/")
        self.group.save()
        self.client.force_authenticate(self.authenticated_user)

        response = self.client.get(_get_list_approved_url())
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(len(response.json()["results"]) > 0)

    def test_list_unapproved_unauthorized(self):
        """Users with regular permissions should not be able to see unapproved quotes"""
        self.group.permissions.remove("/sudo/admin/quotes/edit/")
        self.group.save()
        self.client.force_authenticate(self.authenticated_user)

        response = self.client.get(_get_list_unapproved_url())
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.json()["results"]), 0)


def test_detail_authenticated_with_created_by(self):
    """Users with permissions should be able to see detailed quotes
    and verify created_by field behavior"""
    self.client.force_authenticate(self.authenticated_user)

    # Check quote created by self has created by
    response_4 = self.client.get(_get_detail_url(4))
    self.assertEqual(response_4.status_code, status.HTTP_200_OK)
    response_data_4 = response_4.json()

    self.assertIn("created_by", response_data_4)
    self.assertIsInstance(response_data_4["created_by"], dict)
    self.assertEqual(
        response_data_4["created_by"].get("id"), self.authenticated_user.id
    )

    # Quote created by other does not
    response_5 = self.client.get(_get_detail_url(5))
    self.assertEqual(response_5.status_code, status.HTTP_200_OK)
    response_data_5 = response_5.json()

    self.assertIn("created_by", response_data_5)
    self.assertIsNone(response_data_5["created_by"])
