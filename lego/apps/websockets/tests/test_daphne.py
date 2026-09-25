import importlib

from django.test import SimpleTestCase


class DaphneImportTestCase(SimpleTestCase):
    def test_daphne_server_imports(self):
        """
        The websocket service runs under daphne, which nothing else imports, so
        a dependency bump that breaks it would otherwise pass CI.
        """
        importlib.import_module("daphne.server")
