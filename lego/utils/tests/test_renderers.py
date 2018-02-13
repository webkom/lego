from lego.utils.renderers import JSONRenderer
from lego.utils.test_utils import BaseTestCase


class JSONRendererTestCase(BaseTestCase):
    def setUp(self):
        self.renderer = JSONRenderer()

    def test_empty_data(self):
        """The renderer should return an empty object when data is None"""
        self.assertEquals(self.renderer.render(None), '{}'.encode())
