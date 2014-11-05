# -*- coding: utf--8 -*-
from django.test import TestCase

from lego.users.models import User
from lego.app.articles.models import Article

class ArticleTestCase(TestCase):
    fixtures = ['test_users.yaml', 'test_articles.yaml']

    def setUp(self):
        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.article = Article.objects.get(id=1)
        #self.article = Article.objects.get(id=2)

    def testAuthor(self):
        self.assertEqual(self.article.author, self.user1)
        self.assertNotEqual(self.article.author, self.user2)

