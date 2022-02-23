from django.urls import reverse
from rest_framework import status

from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_list_url():
    return reverse("api:v1:company-list")


def _get_detail_url(pk):
    return reverse("api:v1:company-detail", kwargs={"pk": pk})


class CompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)

    def test_list_with_any_user(self):
        company_response = self.client.get(_get_list_url())
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)

    def test_detail_with_any_user(self):
        company_response = self.client.get(_get_detail_url(1))
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)

    def test_nonexsisting_unsafe_methods(self):
        self.client.force_authenticate(self.abakus_user)
        self.assertEqual(
            self.client.post(_get_list_url(), {"name": "test"}).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.patch(_get_detail_url(1), {"name": "test"}).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(_get_detail_url(1)).status_code,
            status.HTTP_403_FORBIDDEN,
        )
