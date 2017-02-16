from django.test import TestCase

from lego.apps.ical.models import ICalToken
from lego.apps.users.models import User


class TokenTestCase(TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_meetings.yaml',
                'test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)

    def test_generate_initial_token(self):
        token = ICalToken.objects.get_or_create(user=self.user)[0]
        self.assertEqual(token.user, self.user)
        self.assertEqual(len(token.token), 64)

    def test_regenerate_token(self):
        token = ICalToken.objects.get_or_create(user=self.user)[0]
        token_old = token.token
        token.delete()
        token = ICalToken.objects.create(user=self.user)
        self.assertNotEqual(token.token, token_old)
        self.assertEqual(len(token.token), 64)
