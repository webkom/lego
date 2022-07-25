import functools
from datetime import datetime, timezone

from django.test import TestCase
from rest_framework.test import APITestCase, APITransactionTestCase


class BaseTestCase(TestCase):
    pass


class BaseAPITestCase(APITestCase):
    pass


class BaseAPITransactionTestCase(APITransactionTestCase):
    pass


class ViewTestCase(BaseTestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


def fake_time(y, m, d):
    dt = datetime(y, m, d)
    return dt.replace(tzinfo=timezone.utc)


def async_test(f):
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(*args, **kwargs):
            return await f(*args, **kwargs)

        return wrapped

    return wrapper
