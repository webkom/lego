# -*- coding: utf8 -*-
from django.test import TestCase
from oauth2_provider.models import Application

from lego.app.oauth.models import APIApplication


class APIApplicationTestCase(TestCase):
    fixtures = ['initial_users.yaml', 'initial_applications.yaml']

    def test_initial_application(self):
        api_app = APIApplication.objects.get(pk=1)
        self.assertTrue(len(api_app.description))
        self.assertEqual(api_app.authorization_grant_type, Application.GRANT_PASSWORD)
