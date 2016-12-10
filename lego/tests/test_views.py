from django.core.urlresolvers import reverse

from lego.utils.test_utils import ViewTestCase


class SmokeTest(ViewTestCase):

    def test_landing_page(self):
        response = self.client.get(reverse('landing_page'))
        self.assertStatusCode(response)
