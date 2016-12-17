from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from lego.apps.health.permissions import HealthPermission


@override_settings(HEALTH_CHECK_REMOTE_IPS=[
    '129.241.',
    '127.0.0.'
])
class HealthPermissionTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.permission_class = HealthPermission()

    def test_unknown_ip(self):
        request = self.factory.get('/health/')
        request.META['REMOTE_ADDR'] = '100.0.1.1'
        self.assertFalse(self.permission_class.has_permission(request, None))

    def test_localhost(self):
        request = self.factory.get('/health/')
        self.assertTrue(self.permission_class.has_permission(request, None))

    def test_allowed_ip(self):
        request = self.factory.get('/health/')
        request.META['REMOTE_ADDR'] = '129.241.208.1'
        self.assertTrue(self.permission_class.has_permission(request, None))
