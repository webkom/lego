from rest_framework.test import APITestCase

from lego.apps.flatpages.models import Page


class PageAPITestCase(APITestCase):
    fixtures = ['pages.yaml']

    def setUp(self):
        self.pages = Page.public_objects.all().order_by('created_at')

    def test_get_pages(self):
        response = self.client.get('/api/v1/pages/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 4)
        first = response.data['results'][0]
        self.assertEqual(first['title'], self.pages.first().title)
        self.assertEqual(first['slug'], self.pages.first().slug)
        self.assertEqual(first['content'], self.pages.first().content)

    def test_get_page_with_id(self):
        slug = 'webkom'
        response = self.client.get('/api/v1/pages/{0}/'.format(slug))
        expected = self.pages.get(slug=slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], expected.title)
        self.assertEqual(response.data['slug'], expected.slug)
        self.assertEqual(response.data['content'], expected.content)

    def test_non_existing_retrieve(self):
        response = self.client.get('/api/v1/pages/badslug/')
        self.assertEqual(response.status_code, 404)

    def test_require_auth_retrieve(self):
        page = Page.objects.create(title='eh', slug='eh', require_auth=True)
        response = self.client.get('/api/v1/pages/{0}/'.format(page.slug))
        self.assertEqual(response.status_code, 404)

    def test_hierarchy(self):
        slug = 'webkom'
        response = self.client.get('/api/v1/pages/{0}/hierarchy/'.format(slug))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        for page in response.data:
            # Make sure we're not retrieving siblings:
            self.assertNotEqual(page['slug'], 'bedkom')
