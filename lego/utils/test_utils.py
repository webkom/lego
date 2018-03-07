from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APITransactionTestCase


class BaseTestCase(TestCase):
    """
    Normally we don't want to hit Cassandra in tests, so we mock out add_activity in most tests
    to avoid this. If you want to test something using Cassandra, override FeedTestBase instead.
    """
    pass


class BaseAPITestCase(APITestCase):
    pass


class BaseAPITransactionTestCase(APITransactionTestCase):
    pass


class ViewTestCase(BaseTestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


def fake_time(y, m, d):
    dt = timezone.datetime(y, m, d)
    dt = timezone.pytz.timezone('UTC').localize(dt)
    return dt
