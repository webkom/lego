# -*- coding: utf8 -*-
from django.test import TestCase


class ViewTestCase(TestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)
