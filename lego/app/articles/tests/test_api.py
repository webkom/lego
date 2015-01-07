# -*- coding: utf8 -*-
from rest_framework.test import APITestCase, APIRequestFactory

from lego.users.models import User
from lego.app.articles.models import Article
from lego.app.articles.views.articles import ArticlesViewSet

class GetArticleAPITestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml','initial_users.yaml',
                'test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.article = Article.objects.get(id=1)
        self.user = User.objects.get(id=1)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/articles')
        self.view = ArticlesViewSet.as_view({'get': 'retrieve'})

    def testCanView(self):
        response = self.view(self.factory.get('/api/articles/1'), pk=self.article.pk, user=self.user)
        self.assertEqual(response.status_code, 404)

