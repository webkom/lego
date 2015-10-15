from django.test import TestCase

from lego.apps.articles.models import Article
from lego.apps.articles.views.articles import ArticlesViewSet
from lego.apps.content.tests import ContentTestMixin
from lego.apps.users.models import User


class ArticleTest(TestCase, ContentTestMixin):
    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_quotes.yaml']

    model = Article
    ViewSet = ArticlesViewSet

    def test_str(self):
        item = self.model.objects.all().get(id=1)
        author = User.objects.all().get(id=1)
        self.assertEqual(str(item), item.title +
                         '(by: ' + str(author) + ')')
