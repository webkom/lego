from django.db import models
from django.test import testcases
from django.utils.text import slugify

from lego.apps.users.models import User
from lego.apps.articles.models import Article
from lego.apps.content.models import SlugModel


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

class ContentModelTestCase(testcases.TestCase):
    fixtures = ['initial_abakus_groups.yaml', 'initial_files.yaml',
                'initial_users.yaml', 'test_articles.yaml']

    def test_parse_content(self):
        content = (
            '<p>some <b>cool</b> text telling you to come to this party</p>'
            '<p>psst.. We got free <strike>dranks!</strike>drinks</p>'
        )
        article = Article(
            title='test content',
            description='test description',
            content=content,
            author=User.objects.get(username='webkom')
        )
        article.save()
        self.assertEqual(article.content, content)


    def test_parse_content_strip_unsafe_values(self):
        content = (
            '<p>some <b>cool</b> text telling you to come to this party</p>'
            '<p><script>window.alert("I am a virus")</script></p>'
        )
        article = Article(
            title='test content',
            description='test description',
            content=content,
            author=User.objects.get(username='webkom')
        )
        article.save()
        self.assertTrue('<script>' not in article.content)

    def test_parse_content_strip_css_values(self):
        content = (
            '<p>some <b>cool</b> text telling you to come to this party</p>'
                '<p style="color: red;">psst.. We got free <strike>dranks!</strike>drinks</p>'
        )
        article = Article(
            title='test content',
            description='test description',
            content=content,
            author=User.objects.get(username='webkom')
        )
        article.save()
        self.assertTrue('style="color: red;"' not in article.content)

    def test_parse_content_handle_images(self):
        content=(
            '<p>some <b>cool</b> text telling you to come to this party</p>',
            '<p><img data-file-key="default_male_avatar.png" src="dont_store_this_url.png" /></p>',
            '<p>psst.. We got free <strike>dranks!</strike>drinks</p>'
        )

        article = Article(
            title='test content',
            description='test description',
            content=content,
            author=User.objects.get(username='webkom')
        )
        article.save()
        self.assertTrue('src="http://localhost:8888/' in article.content)

