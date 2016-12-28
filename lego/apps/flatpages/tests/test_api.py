from rest_framework.test import APITestCase

from lego.apps.flatpages.models import Page


class PageAPITestCase(APITestCase):
    fixtures = ['pages.yaml']

    def setUp(self):
        self.pages = Page.public_objects.all().order_by('created_at')

    def test_get_pages(self):
        response = self.client.get('/api/v1/pages/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        first = response.data['results'][0]
        self.assertEqual(first['title'], self.pages.first().title)
        self.assertEqual(first['slug'], self.pages.first().slug)
        self.assertEqual(first['content'], self.pages.first().content)

    def test_get_page_with_id(self):
        response = self.client.get('/api/v1/pages/bedkom/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.pages.get(pk=2).title)
        self.assertEqual(response.data['slug'], self.pages.get(pk=2).slug)
        self.assertEqual(response.data['content'], self.pages.get(pk=2).content)

    def test_require_auth(self):
        response = self.client.get('/api/v1/pages/badslug/')
        self.assertEqual(response.status_code, 404)
