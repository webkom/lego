from unittest import mock

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from lego.apps.files.fields import FileField
from lego.apps.files.models import File


class FileFieldTestCase(TestCase):

    fixtures = ['test_files.yaml']

    def setUp(self):
        self.field = FileField()
        self.file = File.objects.get(key='abakus.png')

    def test_options(self):
        field = FileField(allowed_types=['image'])
        self.assertEqual(field.allowed_types, ['image'])

    @mock.patch('lego.apps.files.fields.storage.generate_signed_url')
    def test_to_representation(self, mock_generate_signed_url):
        """To representation should return a presigned get"""
        file_mock = mock.Mock()
        self.assertEqual(
            self.field.to_representation(file_mock), mock_generate_signed_url.return_value
        )
        mock_generate_signed_url.assert_called_once_with(File.bucket, file_mock.pk)

    def test_to_internal_value(self):
        """Make sure to_internal_value only accepts a key with valid token"""
        self.assertRaises(ValidationError, self.field.to_internal_value, 'file.png')
        self.assertRaises(ValidationError, self.field.to_internal_value, 'file.png:')
        self.assertRaises(ValidationError, self.field.to_internal_value, 'file.png:token:')

        self.assertEqual(self.field.to_internal_value('abakus.png:token'), self.file)
        self.assertRaises(ValidationError, self.field.to_internal_value, 'abakus.png:_token')
