from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APITransactionTestCase


class BaseTestCase(TestCase):
    """
    Normally we don't want to hit Cassandra in tests, so we mock out add_activity in most tests
    to avoid this. If you want to test something using Cassandra, override FeedTestBase instead.
    """

    def _pre_setup(self):
        super()._pre_setup()
        self._add_activity_mock = patch('lego.apps.feed.feed_manager.feed_manager.add_activity')
        self._add_activity_mock.start()

    def _post_teardown(self):
        super()._post_teardown()
        self._add_activity_mock.stop()


class BaseAPITestCase(APITestCase):
    def _pre_setup(self):
        super()._pre_setup()
        self._add_activity_mock = patch('lego.apps.feed.feed_manager.feed_manager.add_activity')
        self._add_activity_mock.start()

    def _post_teardown(self):
        super()._post_teardown()
        self._add_activity_mock.stop()


class BaseAPITransactionTestCase(APITransactionTestCase):
    def _pre_setup(self):
        super()._pre_setup()
        self._add_activity_mock = patch('lego.apps.feed.feed_manager.feed_manager.add_activity')
        self._add_activity_mock.start()

    def _post_teardown(self):
        super()._post_teardown()
        self._add_activity_mock.stop()


class ViewTestCase(BaseTestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


def fake_time(y, m, d):
    dt = timezone.datetime(y, m, d)
    dt = timezone.pytz.timezone('UTC').localize(dt)
    return dt
