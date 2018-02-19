from django.test import TestCase

from lego.apps.admissions.models import Committee
from lego.apps.users.models import AbakusGroup
from django.urls import reverse
from rest_framework.test import APITestCase

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.users.models import AbakusGroup, User


class CommitteeTestCase(TestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_committees.yaml'
    ]

    def setUp(self):
        pass

    def test_test(self):
        self.assertEqual(Committee.objects.first().group, AbakusGroup.objects.get(name="Webkom"))





def _get_list_url():
    return reverse('api:v1:admission-list')


def _get_detail_url(pk):
    return reverse('api:v1:admission-detail', kwargs={'pk': pk})


class ListAdmissionTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()

    def test_user(self):
        webkom_user = self.all_users.first()
        AbakusGroup.objects.get(name="Webkom").add_user(webkom_user)
        self.client.force_authenticate(user=webkom_user)
        response = self.client.get(_get_list_url())
        self.assertEquals(response.status_code, 200)
        print(response.data)
