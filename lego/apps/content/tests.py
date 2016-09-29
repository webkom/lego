from unittest import mock

from django.utils.text import slugify


class SlugContentTestMixin:
    @mock.patch('django.db.models.Model.save')
    def test_slug(self, mock_save):
        self.item = self.model(id=1, title='CORRECTSLUG')

        self.assertIsNone(self.item.slug)
        self.item.save()
        self.assertNotEqual('1-CORRECTSLUG', self.item.slug)
        self.assertEqual('1-correctslug', self.item.slug)
        self.assertEqual(slugify('1-CORRECTSLUG'), self.item.slug)
        mock_save.assert_called_with()
