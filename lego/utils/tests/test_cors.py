from datetime import timedelta

from django.test.utils import override_settings
from django.utils import timezone

from corsheaders.middleware import (
    ACCESS_CONTROL_ALLOW_CREDENTIALS,
    ACCESS_CONTROL_ALLOW_HEADERS,
    ACCESS_CONTROL_ALLOW_METHODS,
    ACCESS_CONTROL_ALLOW_ORIGIN,
    ACCESS_CONTROL_EXPOSE_HEADERS,
    ACCESS_CONTROL_MAX_AGE,
)

from lego.utils.cors import generate_cors_origin_regex_list
from lego.utils.test_utils import BaseTestCase

cors_origin_domains = ["abakus.no", "webkom.dev"]

valid_origins = [
    # For abakus.no
    "http://abakus.no",
    "http://www.abakus.no",
    "http://webkom.abakus.no",
    "http://webapp-staging.abakus.no",
    "http://long.webkom.abakus.no",
    "https://abakus.no",
    "https://www.abakus.no",
    "https://webkom.abakus.no",
    "https://webapp-staging.abakus.no",
    "https://long.webkom.abakus.no",
    # For webkom.dev
    "http://webkom.dev",
    "http://www.webkom.dev",
    "http://webkom.webkom.dev",
    "http://long.webkom.webkom.dev",
    "https://webkom.dev",
    "https://www.webkom.dev",
    "https://webkom.webkom.dev",
    "https://long.webkom.webkom.dev",
]

invalid_origins = [
    "http://random-website.no",
    "http://invalid.random-website.no",
    "http://randomdomain.no",
    "https://www.test.012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789",
    "https://012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789.com",
    "http://m*y.example.com",
    "http://*my.example.com",
    "http://.example.com",
    "http://example.com*",
    "http://-.com",
    "http://z-.com",
    "https://my.best-example*.best-example*.com",
    "http://127*.0.0.1",
    "https://my.*.com",
]


class CorsTest(BaseTestCase):
    @override_settings(
        CORS_ALLOW_METHODS=["OPTIONS"],
        CORS_ALLOW_CREDENTIALS=True,
        CORS_ORIGIN_REGEX_WHITELIST=generate_cors_origin_regex_list(
            cors_origin_domains
        ),
    )
    def test_valid_cors_origins(self):
        for valid_origin in valid_origins:
            resp = self.client.options("/", HTTP_ORIGIN=valid_origin)
            assert resp[ACCESS_CONTROL_ALLOW_ORIGIN] == valid_origin

    @override_settings(
        CORS_ALLOW_METHODS=["OPTIONS"],
        CORS_ALLOW_CREDENTIALS=True,
        CORS_ORIGIN_REGEX_WHITELIST=generate_cors_origin_regex_list(
            cors_origin_domains
        ),
    )
    def test_invalid_cors_origins(self):
        for invalid_origin in invalid_origins:
            resp = self.client.options("/", HTTP_ORIGIN=invalid_origin)
            assert ACCESS_CONTROL_ALLOW_ORIGIN not in resp
