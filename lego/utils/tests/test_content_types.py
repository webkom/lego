from unittest import mock

from django.test import TestCase

from lego.utils.content_types import instance_to_string


class ContentTypesTestCase(TestCase):

    def setUp(self):
        self.instance = mock.Mock()
        self.instance.id = '10'
        self.instance._meta.app_label = 'utils'
        self.instance._meta.model_name = 'mock'

    def test_instance_to_string(self):
        self.assertEqual(instance_to_string(self.instance), 'utils.mock-10')
