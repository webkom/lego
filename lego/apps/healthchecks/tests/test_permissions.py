from django.test import override_settings
from django.test.client import RequestFactory

from lego.apps.healthchecks.permissions import HealthChecksPermission
from lego.utils.test_utils import BaseTestCase


# Only allow localhost
@override_settings(HEALTH_CHECK_REMOTE_IPS=["127.0.0."])
class HealthCheckPermissionTestCase(BaseTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission_class = HealthChecksPermission()

    def test_unknown_ip(self):
        request = self.factory.get("/healthchecks/")
        request.META["REMOTE_ADDR"] = "100.0.1.1"
        self.assertFalse(self.permission_class.has_permission(request, None))

    def test_localhost(self):
        request = self.factory.get("/healthchecks/")
        self.assertTrue(self.permission_class.has_permission(request, None))
