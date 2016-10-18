from rest_framework.test import APITestCase

from lego.apps.flatpages.models import Page


class PageAPITestCase(APITestCase):
    fixtures = ['pages.yaml']

    def setUp(self):
        self.pages = Page.public_objects.all().order_by('created_by')

    def test_get_pages(self):
        response = self.client.get('/api/v1/pages/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.pages.first().title)
        self.assertEqual(response.data[0]['slug'], self.pages.first().slug)
        self.assertEqual(response.data[0]['content'], self.pages.first().content)
        self.assertEqual(response.data[0]['toc'], self.pages.first().toc)

    def test_get_page_with_id(self):
        response = self.client.get('/api/v1/pages/2/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.pages.get(pk=2).title)
        self.assertEqual(response.data['slug'], self.pages.get(pk=2).slug)
        self.assertEqual(response.data['content'], self.pages.get(pk=2).content)
        self.assertEqual(response.data['toc'], self.pages.get(pk=2).toc)

    def test_require_auth(self):
        response = self.client.get('/api/v1/pages/3/')
        self.assertEqual(response.status_code, 404)
