import json

from rest_framework.test import APITestCase

from lego.app.flatpages.models import Page


class PageAPITestCase(APITestCase):
    fixtures = ['pages.yaml']

    def setUp(self):
        self.pages = Page.public_objects.all()

    def test_get_pages(self):
        response = self.client.get('/api/v1/pages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], self.pages.first().title)
        self.assertEqual(data[0]['slug'], self.pages.first().slug)
        self.assertEqual(data[0]['content'], self.pages.first().content)
        self.assertEqual(data[0]['toc'], self.pages.first().toc)
        self.assertEqual(data[0]['require_auth'], self.pages.first().require_auth)

    def test_get_page_with_id(self):
        response = self.client.get('/api/v1/pages/2/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['title'], self.pages.get(pk=2).title)
        self.assertEqual(data['slug'], self.pages.get(pk=2).slug)
        self.assertEqual(data['content'], self.pages.get(pk=2).content)
        self.assertEqual(data['toc'], self.pages.get(pk=2).toc)
        self.assertEqual(data['require_auth'], self.pages.get(pk=2).require_auth)

    def test_require_auth(self):
        response = self.client.get('/api/v1/pages/3/')
        self.assertEqual(response.status_code, 404)
