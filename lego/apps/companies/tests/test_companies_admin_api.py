from datetime import datetime
from zoneinfo import ZoneInfo

from django.urls import reverse
from rest_framework import status

from lego.apps.companies.models import (
    Company,
    CompanyInterest,
    Semester,
    StudentCompanyContact,
)
from lego.apps.events.constants import SUCCESS_REGISTER, SUCCESS_UNREGISTER
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.joblistings.models import Joblisting
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase

_test_company_data = [{"name": "TEST"}, {"name": "TEST2"}]

_test_semester_files_data = [{"semester": 2, "company": 1}]

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


def _get_bdb_event_statistics_url(pk):
    return reverse("api:v1:bdb-event-statistics", kwargs={"pk": pk})


def _get_semester_files_list_url(company_pk):
    return reverse("api:v1:semester-files-list", kwargs={"company_pk": company_pk})


def _get_semester_files_detail_url(company_pk, pk):
    return reverse(
        "api:v1:semester-files-detail", kwargs={"company_pk": company_pk, "pk": pk}
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
        return StudentCompanyContact.objects.filter(company=pk).count()

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


class CreateSemesterFilesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_semester_files_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(
            _get_semester_files_list_url(1), _test_semester_files_data[0]
        )
        self.assertEqual(company_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_semester_files_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_semester_files_list_url(1), _test_semester_files_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_semester_files_update_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_semester_files_detail_url(1, 1), _test_semester_files_data[0]
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_semester_files_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_semester_files_detail_url(1, 1), _test_semester_files_data[0]
        )
        self.assertEqual(company_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            company_response.json()["semester"],
            _test_semester_files_data[0]["semester"],
        )


class DeleteSemesterFilesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_semester_files_deletion_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_semester_files_detail_url(1, 1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_semester_files_deletion_with_bedkom_user(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_semester_files_detail_url(1, 1))
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


def _create_event(company, event_type, start_time):
    return Event.objects.create(
        title="Event",
        company=company,
        event_type=event_type,
        start_time=start_time,
        end_time=start_time,
    )


def _create_joblisting(company, visible_from):
    return Joblisting.objects.create(
        title="Joblisting",
        company=company,
        visible_from=visible_from,
        visible_to=visible_from,
        job_type="full_time",
    )


def _create_company_interest(company, semesters):
    company_interest = CompanyInterest.objects.create(
        company=company, contact_person="Test", mail="test@test.no"
    )
    company_interest.semesters.add(*semesters)
    return company_interest


class InferSemesterStatusTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.spring = Semester.objects.get(semester="spring", year=2017)
        self.autumn = Semester.objects.get(semester="autumn", year=2017)
        oslo = ZoneInfo("Europe/Oslo")
        self.facebook = Company.objects.get(name="Facebook")
        self.itera = Company.objects.get(name="Itera")

        _create_event(self.facebook, "course", datetime(2017, 3, 1, tzinfo=oslo))
        _create_event(self.facebook, "course", datetime(2017, 4, 1, tzinfo=oslo))
        _create_event(
            self.facebook, "company_presentation", datetime(2017, 9, 1, tzinfo=oslo)
        )
        _create_company_interest(self.facebook, [self.spring])
        _create_company_interest(self.itera, [self.autumn])

    def _get_semester_statuses(self, response, company):
        company_data = next(
            data for data in response.json()["results"] if data["id"] == company.pk
        )
        return company_data["semesterStatuses"]

    def test_infer_semester_statuses(self):
        self.assertEqual(
            self.facebook.infer_semester_statuses([self.spring, self.autumn]),
            {
                self.spring.pk: ["course", "interested"],
                self.autumn.pk: ["company_presentation"],
            },
        )

    def test_events_are_placed_by_local_time(self):
        # 31 July 23:30 UTC is 1 August in Oslo, which is in the autumn semester
        _create_event(
            self.itera, "course", datetime(2017, 7, 31, 23, 30, tzinfo=ZoneInfo("UTC"))
        )
        self.assertEqual(
            self.itera.infer_semester_statuses([self.spring, self.autumn]),
            {self.spring.pk: [], self.autumn.pk: ["course", "interested"]},
        )

    def test_job_postings_are_placed_by_visible_from(self):
        oslo = ZoneInfo("Europe/Oslo")
        _create_joblisting(self.itera, datetime(2017, 2, 1, tzinfo=oslo))
        # 31 July 23:30 UTC is 1 August in Oslo, which is in the autumn semester
        _create_joblisting(
            self.facebook, datetime(2017, 7, 31, 23, 30, tzinfo=ZoneInfo("UTC"))
        )
        self.assertEqual(
            self.itera.infer_semester_statuses([self.spring, self.autumn]),
            {self.spring.pk: ["job_posting"], self.autumn.pk: ["interested"]},
        )
        self.assertEqual(
            self.facebook.infer_semester_statuses([self.spring, self.autumn]),
            {
                self.spring.pk: ["course", "interested"],
                self.autumn.pk: ["company_presentation", "job_posting"],
            },
        )

    def test_deleted_events_and_interests_are_ignored(self):
        self.facebook.events.get(event_type="company_presentation").delete()
        self.facebook.company_interests.get().delete()
        self.assertEqual(
            self.facebook.infer_semester_statuses([self.spring, self.autumn]),
            {self.spring.pk: ["course"], self.autumn.pk: []},
        )

    def test_list_semester_statuses(self):
        response = self.client.get(_get_bdb_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            self._get_semester_statuses(response, self.facebook),
            [
                {"semester": self.spring.pk, "statuses": ["course", "interested"]},
                {"semester": self.autumn.pk, "statuses": ["company_presentation"]},
            ],
        )
        self.assertEqual(
            self._get_semester_statuses(response, Company.objects.get(name="Webkom")),
            [],
        )

    def test_list_semester_statuses_for_semester(self):
        response = self.client.get(_get_bdb_list_url(), {"semester_id": self.autumn.pk})
        self.assertEqual(
            self._get_semester_statuses(response, self.facebook),
            [{"semester": self.autumn.pk, "statuses": ["company_presentation"]}],
        )

    def test_detail_semester_statuses_and_files(self):
        response = self.client.get(_get_bdb_detail_url(self.facebook.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            response.json()["semesterStatuses"],
            [
                {"semester": self.spring.pk, "statuses": ["course", "interested"]},
                {"semester": self.autumn.pk, "statuses": ["company_presentation"]},
            ],
        )
        self.assertEqual(
            [files["semester"] for files in response.json()["semesterFiles"]],
            [self.spring.pk],
        )


class FilterCompaniesTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def _filter_by_status(self, params):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.get(_get_bdb_list_url(), params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return sorted(company["name"] for company in response.json()["results"])

    def _create_status_data(self):
        oslo = ZoneInfo("Europe/Oslo")
        spring, autumn = Semester.objects.order_by("pk")
        facebook, itera, webkom = Company.objects.order_by("pk")
        _create_event(facebook, "course", datetime(2017, 3, 1, tzinfo=oslo))
        _create_event(itera, "company_presentation", datetime(2017, 9, 1, tzinfo=oslo))
        _create_company_interest(itera, [spring])
        _create_company_interest(webkom, [autumn])

    def test_filter_by_status_interested(self):
        self._create_status_data()
        self.assertEqual(
            self._filter_by_status({"status": "interested", "semester_id": 1}),
            ["Itera"],
        )

    def test_filter_by_status_event_type(self):
        self._create_status_data()
        self.assertEqual(
            self._filter_by_status({"status": "course", "semester_id": 1}),
            ["Facebook"],
        )
        self.assertEqual(
            self._filter_by_status({"status": "course", "semester_id": 2}), []
        )

    def test_filter_by_status_job_posting(self):
        self._create_status_data()
        oslo = ZoneInfo("Europe/Oslo")
        webkom = Company.objects.get(name="Webkom")
        _create_joblisting(webkom, datetime(2017, 2, 1, tzinfo=oslo))
        self.assertEqual(
            self._filter_by_status({"status": "job_posting", "semester_id": 1}),
            ["Webkom"],
        )
        self.assertEqual(
            self._filter_by_status({"status": "job_posting", "semester_id": 2}), []
        )
        self.assertEqual(self._filter_by_status({"status": "job_posting"}), ["Webkom"])

    def test_filter_by_multiple_statuses(self):
        self._create_status_data()
        self.assertEqual(
            self._filter_by_status(
                {"status": "company_presentation,interested", "semester_id": 2}
            ),
            ["Itera", "Webkom"],
        )

    def test_filter_by_status_without_semester(self):
        self._create_status_data()
        self.assertEqual(
            self._filter_by_status({"status": "interested"}), ["Itera", "Webkom"]
        )

    def test_filter_by_status_empty(self):
        self.assertEqual(
            self._filter_by_status({"status": "", "semester_id": 1}),
            ["Facebook", "Itera", "Webkom"],
        )

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


class CompanyEventStatisticsTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_companies.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        self.company = Company.objects.get(pk=1)
        self.spring = Semester.objects.get(semester="spring", year=2017)
        self.autumn = Semester.objects.get(semester="autumn", year=2017)
        self.users = get_dummy_users(6)

    def _create_event(
        self, start_time, participants, waiting, company=None, capacity=None
    ):
        event = Event.objects.create(
            title="Bedpres",
            company=company or self.company,
            start_time=start_time,
            end_time=start_time,
        )
        pool = Pool.objects.create(
            name="Pool",
            capacity=participants if capacity is None else capacity,
            event=event,
            activation_date=start_time,
        )
        users = iter(self.users)
        for _ in range(participants):
            Registration.objects.create(
                event=event, user=next(users), pool=pool, status=SUCCESS_REGISTER
            )
        for _ in range(waiting):
            Registration.objects.create(
                event=event, user=next(users), status=SUCCESS_REGISTER
            )
        return event

    def _get_statistics(self, from_semester, to_semester):
        return self.client.get(
            _get_bdb_event_statistics_url(self.company.pk),
            {"from_semester": from_semester.pk, "to_semester": to_semester.pk},
        )

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name="Abakus").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self._get_statistics(self.spring, self.autumn)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_statistics_within_semester_range(self):
        oslo = ZoneInfo("Europe/Oslo")
        self._create_event(datetime(2017, 3, 1, tzinfo=oslo), participants=4, waiting=2)
        self._create_event(datetime(2017, 9, 1, tzinfo=oslo), participants=2, waiting=0)
        # Outside the range or hosted by another company
        self._create_event(datetime(2018, 1, 1, tzinfo=oslo), participants=5, waiting=1)
        self._create_event(
            datetime(2017, 3, 1, tzinfo=oslo),
            participants=1,
            waiting=0,
            company=Company.objects.get(pk=2),
        )

        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        response = self._get_statistics(self.spring, self.autumn)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "eventCount": 2,
                "averageParticipants": 3,
                "averageWaitingList": 1,
                "averageFill": 1,
            },
        )

        response = self._get_statistics(self.autumn, self.autumn)
        self.assertEqual(
            response.json(),
            {
                "eventCount": 1,
                "averageParticipants": 2,
                "averageWaitingList": 0,
                "averageFill": 1,
            },
        )

    def test_unregistered_users_are_not_counted(self):
        event = self._create_event(
            datetime(2017, 3, 1, tzinfo=ZoneInfo("Europe/Oslo")),
            participants=2,
            waiting=1,
        )
        event.registrations.filter(pool=None).update(status=SUCCESS_UNREGISTER)
        event.registrations.filter(pool__isnull=False).first().delete()

        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        response = self._get_statistics(self.spring, self.spring)
        self.assertEqual(
            response.json(),
            {
                "eventCount": 1,
                "averageParticipants": 1,
                "averageWaitingList": 0,
                "averageFill": 0.5,
            },
        )

    def test_average_fill(self):
        oslo = ZoneInfo("Europe/Oslo")
        self._create_event(
            datetime(2017, 3, 1, tzinfo=oslo), participants=2, waiting=0, capacity=4
        )
        self._create_event(
            datetime(2017, 4, 1, tzinfo=oslo), participants=3, waiting=1, capacity=3
        )
        # An event with two pools fills based on their combined capacity
        event = self._create_event(
            datetime(2017, 5, 1, tzinfo=oslo), participants=1, waiting=0, capacity=1
        )
        Pool.objects.create(
            name="Pool 2", capacity=3, event=event, activation_date=event.start_time
        )
        # Unlimited capacity is excluded from the fill average
        self._create_event(
            datetime(2017, 6, 1, tzinfo=oslo), participants=2, waiting=0, capacity=0
        )

        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        response = self._get_statistics(self.spring, self.spring)
        self.assertEqual(response.json()["eventCount"], 4)
        self.assertAlmostEqual(response.json()["averageFill"], (0.5 + 1 + 0.25) / 3)

    def test_without_events(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self._get_statistics(self.spring, self.autumn)
        self.assertEqual(
            response.json(),
            {
                "eventCount": 0,
                "averageParticipants": 0,
                "averageWaitingList": 0,
                "averageFill": 0,
            },
        )

    def test_invalid_semester(self):
        AbakusGroup.objects.get(name="Bedkom").add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.get(
            _get_bdb_event_statistics_url(self.company.pk), {"from_semester": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
