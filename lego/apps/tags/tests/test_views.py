from rest_framework import status
from rest_framework.test import APITestCase


class TagViewsTestCase(APITestCase):

    fixtures = ["test_abakus_groups.yaml", "test_tags_data.yaml", "initial_tags.yaml"]

    def test_fetch_popular(self):
        response = self.client.get("/api/v1/tags/popular/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(isinstance(response.data, list))

    def test_fetch_list(self):
        response = self.client.get("/api/v1/tags/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            response.data["results"][0], {"tag": "ababrygg", "usages": 0}
        )

    def test_fetch_detail(self):
        response = self.client.get("/api/v1/tags/ababrygg/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertDictEqual(
            response.data,
            {
                "tag": "ababrygg",
                "usages": 0,
                "related_counts": {
                    "article": 0,
                    "event": 0,
                    "quote": 0,
                    "joblisting": 0,
                    "poll": 0,
                },
            },
        )

    def test_fetch_unknown(self):
        response = self.client.get("/api/v1/tags/notexisting/")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
