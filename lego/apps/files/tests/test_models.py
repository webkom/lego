from unittest import mock

from django.test import TestCase

from lego.apps.files.exceptions import UnknownFileType
from lego.apps.files.models import File


class FileModelTestCase(TestCase):

    fixtures = ['test_files.yaml']

    def test_get_file_type(self):
        self.assertEqual(File.get_file_type('abakus.png'), 'image')
        self.assertEqual(File.get_file_type('abakus.jpg'), 'image')
        self.assertEqual(File.get_file_type('abakus.pdf'), 'document')
        self.assertRaises(UnknownFileType, File.get_file_type, 'abakus.mp3')

    def test_get_file_token(self):
        file = File.objects.get(key='abakus.png')
        self.assertEqual(file.get_file_token(), 'abakus.png:token')

    @mock.patch('lego.apps.files.models.storage.get_available_name', return_value='abakus-1.png')
    @mock.patch('lego.apps.files.models.get_random_string', return_value='random_string')
    def test_create_file(self, mock_get_random_string, mock_get_available_name):
        file = File.create_file('abakus.png')

        self.assertEqual(file.key, mock_get_available_name.return_value)
        self.assertEqual(file.token, mock_get_random_string.return_value)
        self.assertEqual(file.file_type, 'image')
