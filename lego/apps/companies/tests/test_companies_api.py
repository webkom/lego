from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.users.models import AbakusGroup, User

_test_company_data = [
    {
        'name': 'TEST',
        'studentContact': 1
    },
    {
        'name': 'TEST2',
        'studentContact': 2
    }
]

_test_semester_status_data = [
    {
        'semester': 2,
        'company': 1,
        'contactedStatus': ['interested']
    }
]

_test_company_contact_data = [
    {
        'name': 'Test',
        'role': 'Test',
        'mail': 'test@test.no',
        'phone': '12345678',
        'company': 1
    }
]


def _get_list_url():
    return reverse('api:v1:company-list')


def _get_detail_url(pk):
    return reverse('api:v1:company-detail', kwargs={'pk': pk})


def _get_semester_status_list_url(company_pk):
    return reverse('api:v1:semester-status-list', kwargs={'company_pk': company_pk})


def _get_semester_status_detail_url(company_pk, pk):
    return reverse('api:v1:semester-status-detail', kwargs={'company_pk': company_pk, 'pk': pk})


def _get_company_contacts_list_url(company_pk):
    return reverse('api:v1:company-contact-list', kwargs={'company_pk': company_pk})


def _get_company_contacts_detail_url(company_pk, pk):
    return reverse('api:v1:company-contact-detail', kwargs={'company_pk': company_pk, 'pk': pk})


class ListCompaniesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_list_url())
        self.assertEqual(company_response.status_code, 403)

    def test_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_list_url())
        self.assertEqual(company_response.status_code, 200)
        self.assertEqual(len(company_response.data['results']), 3)


class RetrieveCompaniesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_detail_url(1))
        self.assertEqual(company_response.status_code, 403)

    def test_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.get(_get_detail_url(1))
        self.assertEqual(company_response.status_code, 200)


class CreateCompaniesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(_get_list_url(), _test_company_data[0])
        self.assertEqual(company_response.status_code, 403)

    def test_company_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(_get_list_url(), _test_company_data[0])
        self.assertEqual(company_response.status_code, 201)

    def test_company_update_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(_get_detail_url(1), _test_company_data[1])
        self.assertEqual(company_response.status_code, 403)

    def test_company_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(_get_detail_url(1), _test_company_data[1])
        self.assertEqual(company_response.status_code, 200)
        self.assertEqual(company_response.data['name'], _test_company_data[1]['name'])


class DeleteCompaniesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_delete_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        delete_response = self.client.delete(_get_detail_url(1))
        self.assertEqual(delete_response.status_code, 403)

    def test_company_delete_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        delete_response = self.client.delete(_get_detail_url(1))
        self.assertEqual(delete_response.status_code, 204)

        company_response = self.client.get(_get_detail_url(1))
        self.assertEqual(company_response.status_code, 404)


class CreateSemesterStatusTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_semester_status_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.post(
            _get_semester_status_list_url(1), _test_semester_status_data[0]
        )
        self.assertEqual(company_response.status_code, 403)

    def test_semester_status_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_semester_status_list_url(1), _test_semester_status_data[0]
        )
        self.assertEqual(response.status_code, 201)

    def test_semester_status_update_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_semester_status_detail_url(1, 1), _test_semester_status_data[0]
        )
        self.assertEqual(response.status_code, 403)

    def test_semester_status_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_semester_status_detail_url(1, 1), _test_semester_status_data[0]
        )
        self.assertEqual(company_response.status_code, 200)
        self.assertEqual(
            company_response.data['semester'], _test_semester_status_data[0]['semester']
        )


class DeleteSemesterStatusTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_semester_status_deletion_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_semester_status_detail_url(1, 1))
        self.assertEqual(response.status_code, 403)

    def test_semester_status_deletion_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_semester_status_detail_url(1, 1))
        self.assertEqual(response.status_code, 204)


class CreateCompanyContactsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_contact_creation_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_company_contacts_list_url(1), _test_company_contact_data[0]
        )
        self.assertEqual(response.status_code, 403)

    def test_company_contact_creation_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(
            _get_company_contacts_list_url(1), _test_company_contact_data[0]
        )
        self.assertEqual(response.status_code, 201)

    def test_company_contact_update_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.patch(
            _get_company_contacts_detail_url(1, 1), _test_company_contact_data[0]
        )
        self.assertEqual(response.status_code, 403)

    def test_company_contact_update_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        company_response = self.client.patch(
            _get_company_contacts_detail_url(1, 1), _test_company_contact_data[0]
        )
        self.assertEqual(company_response.status_code, 200)
        self.assertEqual(company_response.data['name'], _test_company_contact_data[0]['name'])


class DeleteCompanyContacsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_company_contact_deletion_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_company_contacts_detail_url(1, 1))
        self.assertEqual(response.status_code, 403)

    def test_company_contact_deletion_with_bedkom_user(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        response = self.client.delete(_get_company_contacts_detail_url(1, 1))
        self.assertEqual(response.status_code, 204)
        get_response = self.client.get(_get_company_contacts_detail_url(1, 1))
        self.assertEqual(get_response.status_code, 404)
