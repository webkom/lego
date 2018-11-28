from lego.apps.oauth.models import APIApplication
from lego.utils.test_utils import BaseTestCase
from oauth2_provider.models import Application


class APIApplicationTestCase(BaseTestCase):
    fixtures = ["test_users.yaml", "test_applications.yaml"]

    def test_initial_application(self):
        api_app = APIApplication.objects.get(pk=1)
        self.assertTrue(len(api_app.description))
        self.assertEqual(api_app.authorization_grant_type, Application.GRANT_PASSWORD)
