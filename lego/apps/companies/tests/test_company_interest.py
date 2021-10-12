from django.urls import reverse
from rest_framework import status

from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase

_test_company_interest_data = [
    {
        "id": 1,
        "company_name": "BEKK",
        "contact_person": "Bill Gates",
        "mail": "bekk@abakus.no",
        "semesters": [1, 2, 3],
        "events": ["company_presentation", "course", "lunch_presentation"],
        "other_offers": ["collaboration", "readme"],
        "comment": "webkom",
    },
    {
        "id": 1,
        "company_name": "BEKKerino",
        "contact_person": "Bill Gutes",
        "mail": "bekk@webkom.no",
        "semesters": [1, 2, 3, 4],
        "events": ["course", "lunch_presentation"],
        "other_offers": ["collaboration", "itdagene"],
        "comment": "webkom",
    },
]


def _get_company_semesters():
    return reverse("api:v1:company-semester-list")


def _get_company_interests():
    return reverse("api:v1:company-interest-list")


def _get_detail_company_interest(pk):
    return reverse("api:v1:company-interest-detail", kwargs={"pk": pk})


class ListCompanyInterestTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_company_interest.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_list_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_interest_list_response = self.client.get(_get_company_interests())
        self.assertEqual(
            company_interest_list_response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_list_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_interest_list_response = self.client.get(_get_company_interests())
        self.assertEqual(company_interest_list_response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(company_interest_list_response.json()["results"]))


class CreateCompanyInterestTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_company_interest.yaml",
        "test_users.yaml",
    ]

    def test_create_with_any_user(self):
        response = self.client.post(
            _get_company_interests(), _test_company_interest_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RetrieveSemestersInInterestFormTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_company_interest.yaml",
        "test_users.yaml",
    ]

    def test_retrieve_with_any_user(self):
        response = self.client.get(_get_company_semesters())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DeleteCompanyInterestFromList(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_company_interest.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_delete_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_detail_company_interest(1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_detail_company_interest(1))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        get_response = self.client.get(_get_detail_company_interest(1))
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


class EditCompanyInterest(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_company_interest.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_edit_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_detail_company_interest(1), _test_company_interest_data[1]
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        get_response = self.client.get(_get_detail_company_interest(1))
        self.assertEqual(get_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_detail_company_interest(1), _test_company_interest_data[1]
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        get_response = self.client.get(_get_detail_company_interest(1))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
