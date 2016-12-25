from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:article-list')


def _get_detail_url(pk):
    return reverse('api:v1:article-detail', kwargs={'pk': pk})


class ListArticlesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_articles.yaml',
                'test_users.yaml']

    def setUp(self):
        self.all_users = User.objects.all()

    def test_unauthorized_user(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(len(response.data['results']), 1)

    def test_fields(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        article = response.data['results'][0]
        self.assertEqual(set(PublicArticleSerializer.Meta.fields), set(article.keys()))

    def test_authorized_without_permission(self):
        user = self.all_users.first()

        abakus = AbakusGroup.objects.get(name='Abakus')
        abakus.add_user(user)

        article = Article.objects.get(id=1)
        article.can_view_groups.add(abakus)

        self.client.force_authenticate(user=user)
        response = self.client.get(_get_list_url())
        self.assertEqual(len(response.data['results']), 2)


class RetrieveArticlesTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_articles.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

        self.abakus_group = AbakusGroup.objects.get(pk=1)
        self.abakus_group.add_user(self.abakus_user)

    def test_unauthorized(self):
        response = self.client.get(_get_detail_url(3))
        self.assertEqual(response.status_code, 200)

    def test_with_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(2))
        self.assertEqual(response.status_code, 404)
