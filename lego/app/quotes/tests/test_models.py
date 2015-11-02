from django.test import TestCase

from lego.app.content.tests import ContentTestMixin
from lego.app.quotes.models import Quote, QuoteLike
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
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_quotes.yaml']

    def setUp(self):
        self.user = User.objects.get(username='test1')
        self.admin_user = User.objects.get(username='useradmin_test')
        self.admin_group = AbakusGroup.objects.get(name='QuoteAdminTest')
        self.admin_group.add_user(self.admin_user)
        self.quote = Quote.objects.get(pk=1)

    def test_str(self):
        self.assertEqual(str(self.quote), self.quote.title)

    def test_has_liked(self):
        quote = Quote.objects.get(pk=2)
        self.assertEqual(quote.has_liked(user=self.admin_user), True)

    def test_approve(self):
        quote = self.quote
        quote.approve()
        self.assertEqual(quote.approved, True)

    def test_unapprove(self):
        quote = self.quote
        quote.unapprove()
        self.assertEqual(quote.approved, False)

    def test_can_like(self):
        quote = Quote.objects.get(pk=1)
        self.assertEqual(quote.can_like(user=self.admin_user), True)

    def test_can_unlike(self):
        quote = Quote.objects.get(pk=2)
        self.assertEqual(quote.can_unlike(user=self.admin_user), True)

    def test_cannot_like_quote(self):
        quote = Quote.objects.get(pk=3)
        result = quote.like(user=self.user)
        self.assertEqual(result, False)

    def test_cannot_unlike_quote(self):
        quote = Quote.objects.get(pk=3)
        result = quote.unlike(user=self.user)
        self.assertEqual(result, False)

    def test_like_quote(self):
        quote = Quote.objects.get(pk=1)
        before = quote.likes
        quote.like(user=self.admin_user)
        self.assertEqual(quote.likes, before + 1)

    def test_unlike_quote(self):
        quote = Quote.objects.get(pk=2)
        before = quote.likes
        quote.unlike(user=self.admin_user)
        self.assertEqual(quote.likes, before - 1)
