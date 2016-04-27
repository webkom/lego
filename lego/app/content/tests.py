from unittest import mock

from django.utils.text import slugify

from lego.users.models import User


class ContentTestMixin:
    def test_author(self):
        self.user1 = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.item = self.model.objects.get(id=1)

        self.assertEqual(self.item.author, self.user1)
        self.assertNotEqual(self.item.author, self.user2)

    @mock.patch('django.db.models.Model.save')
    def test_slug(self, mock_save):
        self.item = self.model(id=1, title='CORRECTSLUG')

        self.assertIsNone(self.item.slug)
        self.item.save()
        self.assertNotEqual('1-CORRECTSLUG', self.item.slug)
        self.assertEqual('1-correctslug', self.item.slug)
        self.assertEqual(slugify('1-CORRECTSLUG'), self.item.slug)
        mock_save.assert_called_with()
