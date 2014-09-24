# -*- coding: utf8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase


class SmokeTest(TestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)

    def test_landing_page(self):
        response = self.client.get(reverse('landing_page'))
        self.assertStatusCode(response)
