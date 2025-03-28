from unittest.mock import patch

from lego.utils.functions import request_plausible_statistics
from lego.utils.models import BasisModel
from lego.utils.test_utils import BaseTestCase

model_name = "teststatisticsobject"
custom_path = "testcustompath"

mock_plausible_data = {
    f"{model_name}s": {
        "1": f"{model_name}/1",
        "1-test-slug": f"{model_name}/1-test-slug",
    },
    custom_path: {
        "1": f"{custom_path}/1",
    },
}


def mock_request_plausible(url: str, headers: dict):
    url_path = url.split("&filters=event:page==/")[-1]
    page_url, obj_url = url_path.split("/")
    return mock_plausible_data[page_url][obj_url]


class TestStatisticsObject(BasisModel):
    id = None
    slug = None


@patch("lego.utils.functions._request_plausible", side_effect=mock_request_plausible)
class RequestPlausibleStatisticsTest(BaseTestCase):

    def setUp(self):
        self.instance = TestStatisticsObject()

    def validate_response(self, response, page_url, obj_url):
        self.assertEqual(response, f"{page_url}/{obj_url}")

    def test_id(self, *args):
        self.instance.id = 1
        response = request_plausible_statistics(self.instance)
        self.validate_response(response, page_url=model_name, obj_url=self.instance.id)

    def test_slug(self, *args):
        self.instance.slug = "1-test-slug"
        response = request_plausible_statistics(self.instance)
        self.validate_response(
            response, page_url=model_name, obj_url=self.instance.slug
        )

    def test_url_root(self, *args):
        self.instance.id = 1
        response = request_plausible_statistics(self.instance, url_root=custom_path)
        self.validate_response(response, page_url=custom_path, obj_url=self.instance.id)
