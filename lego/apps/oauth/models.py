import fnmatch
from urllib.parse import urlparse

from django.db import models

from oauth2_provider.models import AbstractApplication

from .permissions import APIApplicationPermissionHandler


class APIApplication(AbstractApplication):
    description = models.CharField(
        "application description", max_length=100, blank=True
    )

    class Meta:
        permission_handler = APIApplicationPermissionHandler()

    def redirect_uri_allowed(self, uri):
        """
        Check if a given URI matches one of the allowed redirect URIs.
        Supports:
        - Space-separated URIs
        - Comma-separated URIs
        - Wildcards (*) in host and path using fnmatch

        Allowed patterns:
        - https://example.com/callback
        - https://*.example.com/callback
        - https://example.com/*
        - https://*.example.com/*

        Not Allowed:
        - *
        - https://*
        - https://*.com
        """
        if not uri:
            return False

        # Support both space and comma separated URIs
        raw_uris = self.redirect_uris.replace(",", " ")
        allowed_uris = [u.strip() for u in raw_uris.split() if u.strip()]

        parsed_uri = urlparse(uri)
        if not parsed_uri.scheme or not parsed_uri.netloc:
            return False

        for allowed_uri in allowed_uris:
            parsed_allowed = urlparse(allowed_uri)

            # Check to avoid universal links such as https://*, to avoid wildcard abuse
            allowed_host = parsed_allowed.hostname or ""
            if allowed_host == "*" or (
                allowed_host.startswith("*.") and len(allowed_host.split(".")) < 3
            ):
                continue

            if parsed_allowed.scheme != parsed_uri.scheme:
                continue

            if not fnmatch.fnmatch(
                parsed_uri.hostname or "", parsed_allowed.hostname or ""
            ):
                continue

            allowed_path = parsed_allowed.path or "/"
            uri_path = parsed_uri.path or "/"
            if not fnmatch.fnmatch(uri_path, allowed_path):
                continue

            if parsed_allowed.port and parsed_allowed.port != parsed_uri.port:
                continue

            return True

        return False
