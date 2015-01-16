from django.test import TestCase
from lego.app.articles.models import Article
from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.content.models import TestMixin


class ArticleTest(TestCase, TestMixin):
    fixtures = ['initial_users.yaml', 'initial_applications.yaml']

    def test_run(self):
        self.model = Article
        self.ViewSet = ArticlesViewSet
        self.do_test()