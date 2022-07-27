from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.events.constants import COMPANY_PRESENTATION, PARTY
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse("api:v1:survey-template-list")


def _get_detail_url(template_type):
    return reverse(
        "api:v1:survey-template-detail", kwargs={"template_type": template_type}
    )


def _get_create_url():
    return reverse("api:v1:survey-list")


def _get_edit_url(pk):
    return reverse("api:v1:survey-detail", kwargs={"pk": pk})


class SurveyTemplateViewSetTestCase(APITestCase):
    fixtures = [
        "test_users.yaml",
        "test_abakus_groups.yaml",
        "test_survey_templates.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username="useradmin_test")
        self.admin_group = AbakusGroup.objects.get(name="Bedkom")
        self.admin_group.add_user(self.admin_user)
        self.regular_user = User.objects.get(username="abakule")

        self.taken_template_type = COMPANY_PRESENTATION
        self.free_template_type = PARTY

        self.taken_template_data = {
            "title": "Survey",
            "event": 5,
            "questions": [],
            "template_type": self.taken_template_type,
        }
        self.free_template_data = {
            "title": "Survey",
            "event": 5,
            "questions": [],
            "template_type": self.free_template_type,
        }

    # Create
    def test_create_admin(self):
        """Admin users should be able to create templates"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_create_url(), self.free_template_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_regular(self):
        """Regular users should not be able to create templates"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(_get_create_url(), self.free_template_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_taken_admin(self):
        """It should not be able to create templates whose template_type already has a template"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_create_url(), self.taken_template_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Fetch detail
    def test_detail_admin(self):
        """Admin users should be able to see detailed templates"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_detail_url(self.taken_template_type))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json())

    def test_detail_regular(self):
        """Users should not be able see detailed templates"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_detail_url(self.taken_template_type))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Fetch list
    def test_list_admin(self):
        """Users with permissions should be able to see templates list view"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_regular(self):
        """Regular users should not be able to see templates list view"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # Edit permissions
    def test_edit_admin(self):
        """Admin users should  be able to edit templates"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(_get_edit_url(1), self.free_template_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_regular(self):
        """Regular users should not be able to edit templates"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(_get_edit_url(1), self.free_template_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
