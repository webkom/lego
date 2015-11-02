from django.test import TestCase

from lego.app.content.tests import ContentTestMixin
from lego.app.quotes.models import Quote
from lego.app.quotes.views.quotes import QuoteViewSet
from lego.users.models import AbakusGroup, User


def get_dummy_users(n):
    users = []

    for i in range(n):
        first_name = last_name = username = email = str(i)
        user = User(username=username, first_name=first_name, last_name=last_name, email=email)
        user.save()
        users.append(user)

    return users


class QuoteTest(TestCase, ContentTestMixin):
    fixtures = ['initial_abakus_groups.yaml', 'initial_users.yaml',
                'test_users.yaml', 'test_quotes.yaml']

    model = Quote
    ViewSet = QuoteViewSet


class QuoteMethodTest(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_quotes.yaml']

    def setUp(self):
        self.user = User.objects.get(username='test1')
        self.admin_user = User.objects.get(username='useradmin_test')
        self.admin_group = AbakusGroup.objects.get(name='QuoteAdminTest')
        self.admin_group.add_user(self.with_permission)
        self.quote = Quote.objects.get(pk=1)

    def test_str(self):
        self.assertEqual(str(self.quote), self.quote.title)

    def test_like_quote(self):
        before = self.quote.likes
        self.quote.like(user=self.admin_user)
        self.assertEqual(self.quote.likes, before + 1)

    def test_unlike_quote(self):
        user = User.objects.get(username='useradmin_test')
        quote = Quote.objects.get(pk=1)
        before = quote.likes
        quote.unlike(user=user)
        self.assertEqual(quote.likes, before - 1)
