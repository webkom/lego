from unittest import mock

from django.test import TestCase

from lego.apps.content.models import SlugContent, SlugModel


class ExampleSlugContent(SlugModel):
    slug_field = 'title'
    title = models.CharField(max_length=255)


class SlugModelTestCase(testcases.TestCase):
    def test_slug(self):
        item = ExampleSlugContent(title='CORRECTSLUG')
        self.assertIsNone(item.slug)
        item.save()
        self.assertNotEqual('{}-CORRECTSLUG'.format(item.id), item.slug)
        self.assertEqual('{}-correctslug'.format(item.id), item.slug)
        self.assertEqual(slugify('{}-CORRECTSLUG'.format(item.id)), item.slug)

    def test_slug_slice(self):
        item = ExampleSlugContent(
            title='hey, come to this cool event and get free drinks all night')
        item.save()
        self.assertEqual('{}-hey-come-to-this-cool-event-and-get-free-drinks'.format(item.id),
                         item.slug)

    def test_slug_slice_when_word_ends_at_max_len(self):
        item = ExampleSlugContent(
            title='hey, come to this cool event and get free driinks heh')
        item.save()
        self.assertEqual('{}-hey-come-to-this-cool-event-and-get-free-driinks'.format(item.id),
                         item.slug)

    def test_slug_static(self):
        item = ExampleSlugContent(
            title='hey come to this cool event and get free drinks all night')
        item.save()
        item.title = 'hi'
        item.save()
        self.assertEqual('{}-hey-come-to-this-cool-event-and-get-free-drinks'.format(item.id),
                         item.slug)
