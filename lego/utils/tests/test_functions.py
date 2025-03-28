from unittest.mock import patch

from lego.utils.functions import request_plausible_statistics
from lego.utils.models import BasisModel
from lego.utils.test_utils import BaseTestCase

model_name = "testpath"
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


class MockPlausibleResponse:
    def __init__(self, page_url: str, obj_url: str):
        self.value = mock_plausible_data[page_url][obj_url]


def mock_request_plausible(url: str, headers: dict):
    url_path = url.split("&filters=event:page==/")[-1]
    page_url, obj_url = url_path.split("/")
    return MockPlausibleResponse(page_url, obj_url)


class TestStatisticsObject(BasisModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = None
        self.slug = None
        self._meta.model_name = model_name


@patch("lego.utils.functions._request_plausible", side_effect=mock_request_plausible)
class RequestPlausibleStatisticsTest(BaseTestCase):

    def setUp(self):
        self.obj = TestStatisticsObject()

    def validate_response(self, response, page_url, obj_url):
        self.assertEqual(response.value, f"{page_url}/{obj_url}")

    def test_id(self, *args):
        self.obj.pk = 1
        response = request_plausible_statistics(self.obj)
        self.validate_response(response, page_url=model_name, obj_url=self.obj.id)

    def test_slug(self, *args):
        self.obj.slug = "1-test-slug"
        response = request_plausible_statistics(self.obj)
        self.validate_response(response, page_url=model_name, obj_url=self.obj.slug)

    def test_url_root(self, *args):
        self.obj.id = 1
        response = request_plausible_statistics(self.obj, url_root=custom_path)
        self.validate_response(response, page_url=custom_path, obj_url=self.obj.id)

    def test_invalid_obj(self, *args):
        self.obj._meta.model_name = None
        with self.assertRaises(ValueError):
            request_plausible_statistics(self.obj)
