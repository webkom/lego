from django.test import TestCase
from django.utils import timezone


class ViewTestCase(TestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


def fake_time(y, m, d):
    dt = timezone.datetime(y, m, d)
    dt = timezone.pytz.timezone('UTC').localize(dt)
    return dt
