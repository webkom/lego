from oauth2_provider.models import Application

from lego.apps.oauth.models import APIApplication
from lego.utils.test_utils import BaseTestCase


class APIApplicationTestCase(BaseTestCase):
    fixtures = ["test_users.yaml", "test_applications.yaml"]

    def test_initial_application(self):
        api_app = APIApplication.objects.get(pk=1)
        self.assertTrue(len(api_app.description))
        self.assertEqual(api_app.authorization_grant_type, Application.GRANT_PASSWORD)


class RedirectURIAllowedTestCase(BaseTestCase):

    def setUp(self):
        self.app = APIApplication(
            name="Test App",
            client_type=APIApplication.CLIENT_PUBLIC,
            authorization_grant_type=APIApplication.GRANT_AUTHORIZATION_CODE,
        )

    def test_exact_match(self):
        self.app.redirect_uris = "https://example.com/callback"
        self.assertTrue(self.app.redirect_uri_allowed("https://example.com/callback"))
        self.assertFalse(self.app.redirect_uri_allowed("https://example.com/other"))

    def test_space_separated_uris(self):
        self.app.redirect_uris = "https://a.com/cb https://b.com/cb"
        self.assertTrue(self.app.redirect_uri_allowed("https://a.com/cb"))
        self.assertTrue(self.app.redirect_uri_allowed("https://b.com/cb"))
        self.assertFalse(self.app.redirect_uri_allowed("https://c.com/cb"))

    def test_comma_separated_uris(self):
        self.app.redirect_uris = "https://a.com/cb, https://b.com/cb"
        self.assertTrue(self.app.redirect_uri_allowed("https://a.com/cb"))
        self.assertTrue(self.app.redirect_uri_allowed("https://b.com/cb"))
        self.assertFalse(self.app.redirect_uri_allowed("https://c.com/cb"))

    def test_mixed_comma_space_separated(self):
        self.app.redirect_uris = "https://a.com/cb, https://b.com/cb https://c.com/cb"
        self.assertTrue(self.app.redirect_uri_allowed("https://a.com/cb"))
        self.assertTrue(self.app.redirect_uri_allowed("https://b.com/cb"))
        self.assertTrue(self.app.redirect_uri_allowed("https://c.com/cb"))

    def test_path_wildcard(self):
        self.app.redirect_uris = "https://example.com/*"
        self.assertTrue(self.app.redirect_uri_allowed("https://example.com/callback"))
        self.assertTrue(self.app.redirect_uri_allowed("https://example.com/any/path"))
        self.assertFalse(self.app.redirect_uri_allowed("https://other.com/callback"))

    def test_subdomain_wildcard(self):
        self.app.redirect_uris = "https://*.example.com/callback"
        self.assertTrue(self.app.redirect_uri_allowed("https://app.example.com/callback"))
        self.assertTrue(self.app.redirect_uri_allowed("https://api.example.com/callback"))
        self.assertFalse(self.app.redirect_uri_allowed("https://example.com/callback"))
        self.assertFalse(self.app.redirect_uri_allowed("https://app.other.com/callback"))

    def test_combined_wildcards(self):
        self.app.redirect_uris = "https://*.example.com/*"
        self.assertTrue(self.app.redirect_uri_allowed("https://app.example.com/callback"))
        self.assertTrue(self.app.redirect_uri_allowed("https://api.example.com/any/path"))
        self.assertFalse(self.app.redirect_uri_allowed("https://example.com/callback"))

    def test_scheme_must_match(self):
        self.app.redirect_uris = "https://example.com/callback"
        self.assertFalse(self.app.redirect_uri_allowed("http://example.com/callback"))

    def test_port_matching(self):
        self.app.redirect_uris = "https://example.com:8080/callback"
        self.assertTrue(self.app.redirect_uri_allowed("https://example.com:8080/callback"))
        self.assertFalse(self.app.redirect_uri_allowed("https://example.com:9090/callback"))
        self.assertFalse(self.app.redirect_uri_allowed("https://example.com/callback"))

    def test_empty_uri(self):
        self.app.redirect_uris = "https://example.com/callback"
        self.assertFalse(self.app.redirect_uri_allowed(""))
        self.assertFalse(self.app.redirect_uri_allowed(None))

    def test_invalid_uri(self):
        self.app.redirect_uris = "https://example.com/callback"
        self.assertFalse(self.app.redirect_uri_allowed("not-a-valid-uri"))
        self.assertFalse(self.app.redirect_uri_allowed("/relative/path"))

