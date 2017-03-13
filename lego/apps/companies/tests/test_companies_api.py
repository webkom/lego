from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:company-list')


def _get_detail_url(pk):
    return reverse('api:v1:company-detail', kwargs={'pk': pk})


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
