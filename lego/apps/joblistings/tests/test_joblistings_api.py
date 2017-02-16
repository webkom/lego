from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from lego.apps.joblistings.models import Joblisting
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:joblisting-list')


def _get_detail_url(pk):
    return reverse('api:v1:joblisting-detail', kwargs={'pk': pk})


class ListJoblistingsTestCase(APITestCase):
    fixtures = ['development_joblistings.yaml', 'test_users.yaml',
                'development_companies.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        joblisting_response = self.client.get(_get_list_url())
        self.assertEqual(joblisting_response.status_code, 200)
        self.assertEqual(len(joblisting_response.data['results']), 3)

    def test_without_user(self):
        joblisting_response = self.client.get(_get_list_url())
        self.assertEqual(joblisting_response.status_code, 200)
        self.assertEqual(len(joblisting_response.data['results']), 3)

    def test_list_after_visible_to(self):
        joblisting = Joblisting.objects.all().first()
        joblisting.visible_to = timezone.now() - timedelta(days=2)
        joblisting.save()
        joblisting_response = self.client.get(_get_list_url())
        self.assertEqual(joblisting_response.status_code, 200)
        self.assertEqual(len(joblisting_response.data['results']), 2)


class RetrieveJoblistingsTestCase(APITestCase):
    fixtures = ['development_joblistings.yaml', 'test_users.yaml',
                'development_companies.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        joblisting_response = self.client.get(_get_detail_url(1))
        self.assertEqual(joblisting_response.data['id'], 1)
        self.assertEqual(joblisting_response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(self.abakus_user)
        joblisting_response = self.client.get(_get_detail_url(2))
        self.assertEqual(joblisting_response.data['id'], 2)
        self.assertEqual(joblisting_response.status_code, 200)
