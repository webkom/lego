# -*- coding: utf--8 -*-
from django.test import TestCase
from lego.app.articles.models import Article
from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.content.tests import TestMixin


class ArticleTest(TestCase, TestMixin):
    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_articles.yaml']

    model = Article
    ViewSet = ArticlesViewSet
