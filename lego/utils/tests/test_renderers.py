from django.test import TestCase

from lego.utils.renderers import JSONRenderer


class JSONRendererTestCase(TestCase):

    def setUp(self):
        self.renderer = JSONRenderer()

    def test_empty_data(self):
        """The renderer should return an empty object when data is None"""
        self.assertEquals(self.renderer.render(None), '{}'.encode())
