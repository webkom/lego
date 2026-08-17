from django.test import Client

import yaml

from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase


class APIDocsTestCase(BaseTestCase):
    """
    Make sure the api docs works like expected.
    """

    fixtures = ["test_users.yaml"]

    def setUp(self):
        self.client = Client()

    def test_get_without_auth(self):
        response = self.client.get("/api-docs/")
        self.assertEqual(200, response.status_code)

    def test_get_with_auth(self):
        self.client.force_login(User.objects.get(username="test1"))
        response = self.client.get("/api-docs/")
        self.assertEqual(200, response.status_code)

    def test_schema_generates_without_errors(self):
        response = self.client.get("/api-docs/schema/")
        self.assertEqual(200, response.status_code)

        schema = yaml.safe_load(response.content)
        self.assertEqual("3.0.3", schema["openapi"])
        self.assertTrue(schema["paths"])

    def test_schema_covers_the_api(self):
        response = self.client.get("/api-docs/schema/")
        paths = yaml.safe_load(response.content)["paths"]

        for endpoint in [
            "/api/v1/events/",
            "/api/v1/events/{id}/",
            "/api/v1/users/",
            "/api/v1/articles/",
            "/api/v1/meetings/",
            "/authorization/token-auth/",
        ]:
            self.assertIn(endpoint, paths)

    def test_schema_uses_camel_case(self):
        response = self.client.get("/api-docs/schema/")
        schemas = yaml.safe_load(response.content)["components"]["schemas"]

        properties = schemas["EventRead"]["properties"]
        self.assertIn("startTime", properties)
        self.assertNotIn("start_time", properties)

        snake_cased = [
            f"{name}.{prop}"
            for name, schema in schemas.items()
            for prop in schema.get("properties", {})
            if "_" in prop
        ]
        self.assertEqual([], snake_cased)
