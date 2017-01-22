from unittest import mock

from django.test import TestCase

from lego.apps.users.models import User
from lego.utils import content_types


class ContentTypesTestCase(TestCase):

    def setUp(self):
        self.instance = mock.Mock()
        self.instance.pk = '10'
        self.instance._meta.app_label = 'utils'
        self.instance._meta.model_name = 'mock'

    def test_instance_to_string(self):
        self.assertEqual(content_types.instance_to_string(self.instance), 'utils.mock-10')

    def test_split_string(self):
        self.assertEquals(
            content_types.split_string('test.model-1'),
            ('test.model', '1')
        )

        self.assertEquals(
            content_types.split_string('test.model-1-2'),
            ('test.model', '1-2')
        )

    def test_string_to_model_cls(self):
        self.assertEquals(
            content_types.string_to_model_cls('users.user'),
            User
        )

        self.assertRaises(
            content_types.VALIDATION_EXCEPTIONS,
            content_types.string_to_model_cls,
            'unknown.model'
        )
