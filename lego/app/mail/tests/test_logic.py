from django.test import TestCase

from ..logic import handle_mail


class LogicTestCase(TestCase):
    def setUp(self):
        pass

    def test_handle_mail(self):
        self.assertEqual(bool(handle_mail("dd", "dew", "fwefwefew")), True)