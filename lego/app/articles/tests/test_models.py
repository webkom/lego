from django.test import TestCase

from lego.app.articles.models import Article
from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.content.models import TestMixin


class ArticleTest(TestCase, TestMixin):

    model = Article
    ViewSet = ArticlesViewSet

