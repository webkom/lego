from django.urls import reverse
from rest_framework import status

from lego.apps.companies.models import StudentCompanyContact
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase

_test_company_data = [{"name": "TEST"}, {"name": "TEST2"}]

_test_semester_status_data = [
    {"semester": 2, "company": 1, "contactedStatus": ["interested"]}
]

_test_company_contact_data = [
    {
        "name": "Test",
        "role": "Test",
        "mail": "test@test.no",
        "phone": "12345678",
        "company": 1,
    }
]


def _get_test_student_contacts_data(pk):
    return [
        {"studentContacts": []},
        {
            "studentContacts": [
                {
                    "company": pk,
                    "user": 1,
                    "semester": 1,
                }
            ]
        },
        {
            "studentContacts": [
                {
                    "company": pk,
                    "user": 1,
                    "semester": 1,
                },
                {
                    "company": pk,
                    "user": 2,
                    "semester": 1,
                },
            ]
        },
    ]


def _get_bdb_list_url():
    return reverse("api:v1:bdb-list")


def _get_bdb_detail_url(pk):
    return reverse("api:v1:bdb-detail", kwargs={"pk": pk})


def _get_semester_status_list_url(company_pk):
    return reverse("api:v1:semester-status-list", kwargs={"company_pk": company_pk})


def _get_semester_status_detail_url(company_pk, pk):
    return reverse(
        "api:v1:semester-status-detail", kwargs={"company_pk": company_pk, "pk": pk}
    )


def _get_company_contacts_list_url(company_pk):
    return reverse("api:v1:company-contact-list", kwargs={"company_pk": company_pk})


def _get_company_contacts_detail_url(company_pk, pk):
    return reverse(
        "api:v1:company-contact-detail", kwargs={"company_pk": company_pk, "pk": pk}
    )


class ListCompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_bdb_list_url())
        self.assertEqual(company_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_bdb_list_url())
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 3)
        self.assertEqual(
            len(company_response.json()["results"][0]["studentContacts"]), 2
        )

    def test_with_semester_query(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_bdb_list_url(), {"semester_id": 1})
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 3)
        self.assertEqual(
            len(company_response.json()["results"][0]["studentContacts"]), 1
        )


class RetrieveCompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_bdb_detail_url(1))
        self.assertEqual(company_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_bdb_detail_url(1))
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)


class CreateCompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(_get_bdb_list_url(), _test_company_data[0])
        self.assertEqual(company_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(_get_bdb_list_url(), _test_company_data[0])
        self.assertEqual(company_response.status_code, status.HTTP_201_CREATED)

    def test_company_update_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_bdb_detail_url(1), _test_company_data[1]
        )
        self.assertEqual(company_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_bdb_detail_url(1), _test_company_data[1]
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(company_response.json()["name"], _test_company_data[1]["name"])


class DeleteCompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_delete_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        delete_response = self.client.delete(_get_bdb_detail_url(1))
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_delete_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        delete_response = self.client.delete(_get_bdb_detail_url(1))
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        company_response = self.client.get(_get_bdb_detail_url(1))
        self.assertEqual(company_response.status_code, status.HTTP_404_NOT_FOUND)


class UpdateStudentCompanyContactTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def getStudentCompanyContactCount(self, pk):
        return StudentCompanyContact.objects.filter(company=2).count()

    def updateCompany(self, pk, body):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(_get_bdb_detail_url(pk), body)
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_add_student_company_contact(self):
        self.assertEqual(self.getStudentCompanyContactCount(2), 0)

        self.updateCompany(2, _get_test_student_contacts_data(2)[1])
        self.assertEqual(self.getStudentCompanyContactCount(2), 1)

    def test_add_multiple_student_company_contacts(self):
        self.assertEqual(self.getStudentCompanyContactCount(2), 0)

        self.updateCompany(2, _get_test_student_contacts_data(2)[1])
        self.assertEqual(self.getStudentCompanyContactCount(2), 1)

        self.updateCompany(2, _get_test_student_contacts_data(2)[2])
        self.assertEqual(self.getStudentCompanyContactCount(2), 2)

    def test_delete_student_company_contacts(self):
        self.assertEqual(self.getStudentCompanyContactCount(2), 0)

        self.updateCompany(2, _get_test_student_contacts_data(2)[2])
        self.assertEqual(self.getStudentCompanyContactCount(2), 2)

        self.updateCompany(2, _get_test_student_contacts_data(2)[1])
        self.assertEqual(self.getStudentCompanyContactCount(2), 1)

        self.updateCompany(2, _get_test_student_contacts_data(2)[0])
        self.assertEqual(self.getStudentCompanyContactCount(2), 0)


class CreateSemesterStatusTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_semester_status_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(
            _get_semester_status_list_url(1), _test_semester_status_data[0]
        )
        self.assertEqual(company_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_semester_status_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_semester_status_list_url(1), _test_semester_status_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_semester_status_update_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_semester_status_detail_url(1, 1), _test_semester_status_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_semester_status_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_semester_status_detail_url(1, 1), _test_semester_status_data[0]
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            company_response.json()["semester"],
            _test_semester_status_data[0]["semester"],
        )


class DeleteSemesterStatusTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_semester_status_deletion_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_semester_status_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_semester_status_deletion_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_semester_status_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CreateCompanyContactsTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_contact_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_company_contacts_list_url(1), _test_company_contact_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_contact_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_company_contacts_list_url(1), _test_company_contact_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_company_contact_update_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_company_contacts_detail_url(1, 1), _test_company_contact_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_contact_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_company_contacts_detail_url(1, 1), _test_company_contact_data[0]
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            company_response.json()["name"], _test_company_contact_data[0]["name"]
        )


class DeleteCompanyContacsTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_contact_deletion_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_company_contacts_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_company_contact_deletion_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_company_contacts_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        get_response = self.client.get(_get_company_contacts_detail_url(1, 1))
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)


class FilterCompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_filter_by_name(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        company_response = self.client.get(_get_bdb_list_url(), {"name": ""})
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 3)

        company_response = self.client.get(_get_bdb_list_url(), {"name": "Face"})
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 1)

        company_response = self.client.get(
            _get_bdb_list_url(), {"name": "Bedrift som ikke finnes"}
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 0)

    def test_filter_by_student_contacts(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        # test empty query params
        company_response = self.client.get(
            _get_bdb_list_url(), {"semester_id": 1, "student_contacts": ""}
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 3)

        # test for single semester_id
        company_response = self.client.get(
            _get_bdb_list_url(), {"semester_id": 1, "student_contacts": "te"}
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 1)

        # test for non-existing user
        company_response = self.client.get(
            _get_bdb_list_url(),
            {"semester_id": 1, "student_contacts": "Bruker som ikke finnes"},
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 0)

        # test without semester_id query param
        company_response = self.client.get(
            _get_bdb_list_url(), {"student_contacts": "te"}
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 2)

    def test_filter_by_status_interested(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(
            _get_bdb_list_url(), {"status": "interested", "semester_id": 1}
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 1)

    def test_filter_by_status_not_interested(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(
            _get_bdb_list_url(), {"status": "not_interested", "semester_id": 1}
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(company_response.json()["results"]), 0)
