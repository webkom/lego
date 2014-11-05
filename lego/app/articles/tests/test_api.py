# -*- coding: utf8 -*-
from rest_framework.test import APITestCase, APIRequestFactory

from lego.users.models import User
from lego.app.articles.models import Article

class GetArticleAPITestCase(APITestCase):
    def setUp(self):
        self.article = Article.objects.get(id=1)
        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)

        self.factory = APIRequestFactory()
        self.request = self.factory.get('/api/users/')

    def testCanView(self):
        response = self.view(self.request, user=self.user1)
        self.assert

