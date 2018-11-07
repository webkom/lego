from django.urls import reverse
from rest_framework import status

from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_list_url():
    return reverse('api:v1:podcasts-list')


def _get_detail_url(pk):
    return reverse('api:v1:podcasts-detail', kwargs={'pk': pk})


class PodcastViewSetTestCase(BaseAPITestCase):
    fixtures = ['test_users.yaml', 'test_abakus_groups.yaml', 'test_podcasts.yaml']

    def setUp(self):
        """Create test users"""
        self.authenticated_user = User.objects.get(username='test1')
        self.group = AbakusGroup.objects_with_text.get(name='PodcastAdminTest')
        self.group.add_user(self.authenticated_user)

        self.unauthenticated_user = User.objects.get(username='test2')

        self.author1 = User.objects.get(username='test1')
        self.author2 = User.objects.get(username='test1')
        self.thanks1 = User.objects.get(username='test1')
        self.thanks2 = User.objects.get(username='test1')

        self.podcast_data = {
            'source': 'www.testsource.com',
            'description': 'TestDescription',
            'authors': [self.author1.pk, self.author2.pk],
            'thanks': [self.thanks1.pk, self.thanks2.pk]
        }

    def test_create_podcast_authenticated(self):
        """A user with permissions should be able to create a podcast"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.post(_get_list_url(), self.podcast_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_podcast_unathenticated(self):
        """A user without persmissions should not be able to create a podcast"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.post(_get_list_url(), self.podcast_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_podcasts_authenticated(self):
        """A user with permissions should be able to list all podcasts"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_podcast_unathenticated(self):
        """A user with no permissions should be able to list all podcasts"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detailed_podcast_authenticated(self):
        """A user with permissions should not be able to retrive the detailed podcast view"""
        self.client.force_authenticate(self.authenticated_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detailed_podcast_unauthenticated(self):
        """A user with no permissions should not be able to retrive the detailed podcast view"""
        self.client.force_authenticate(self.unauthenticated_user)
        response = self.client.get(_get_detail_url(2))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
