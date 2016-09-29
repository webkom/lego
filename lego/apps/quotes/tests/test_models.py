from django.test import TestCase

from lego.apps.quotes.models import Quote
from lego.apps.users.models import AbakusGroup, User


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

    def test_approve(self):
        quote = self.quote
        quote.approve()
        self.assertEqual(quote.approved, True)

    def test_unapprove(self):
        quote = self.quote
        quote.unapprove()
        self.assertEqual(quote.approved, False)
