from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:survey-list')


def _get_detail_url(pk):
    return reverse('api:v1:survey-detail', kwargs={'pk': pk})


class SurveyViewSetTestCase(APITestCase):
    fixtures = ['test_users.yaml', 'test_abakus_groups.yaml', 'test_surveys.yaml',
                'test_events.yaml', 'test_companies.yaml']

    def setUp(self):
        self.admin_user = User.objects.get(username='useradmin_test')
        self.admin_group = AbakusGroup.objects.get(name='Bedkom')
        self.admin_group.add_user(self.admin_user)
        self.regular_user = User.objects.get(username='abakule')
        self.attended_user = User.objects.get(username='test1')
        self.attending_group = AbakusGroup.objects.get(name='Abakus')
        self.attending_group.add_user(self.attended_user)

        self.survey_data = {
            'title': 'Survey',
            'event': 5,
            'questions': [],
        }

    def test_create_admin(self):
        """Admin users should be able to create surveys"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_regular(self):
        """Regular users should not be able to create surveys"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_attended(self):
        """Users who attended the event should still not be able to create a survey"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.post(_get_list_url(), self.survey_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_admin(self):
        """Admin users should be able to see detailed surveys"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_detail_regular(self):
        """Users should not be able see detailed surveys"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_attended(self):
        """Users who attended the event should be able to see the survey"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)

    def test_list_admin(self):
        """Users with permissions should be able to see surveys list view"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_regular(self):
        """Regular users should not be able to see surveys list view"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(_get_list_url())
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_list_attended(self):
        """Users who attended an event should not be able to see surveys list view"""
        self.client.force_authenticate(user=self.attended_user)
        response = self.client.get(_get_list_url())
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)
