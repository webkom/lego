from django.urls import reverse

from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_frontpage():
    return reverse("api:v1:frontpage-list")


class FrontpageAPITestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_companies.yaml",
        "test_users.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        self.user = User.objects.get(username="webkommer")
        webkom = AbakusGroup.objects.get(name="Webkom")
        webkom.add_user(self.user)

    def test_pinned_is_first(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(_get_frontpage())
        self.assertEquals(res.status_code, 200)
        events = res.data["events"]
        self.assertGreater(len(events), 1)
        first = events[0]
        second = events[1]
        # Check that the first event is pinned
        self.assertTrue(first["pinned"])
        # .. but that the second is before the first
        self.assertGreater(first["startTime"], second["startTime"])

    def test_pinned_is_first_not_logged_in(self):
        res = self.client.get(_get_frontpage())
        self.assertEquals(res.status_code, 200)
        events = res.data["events"]
        self.assertGreater(len(events), 1)
        first = events[0]
        second = events[1]
        # Check that the first event is pinned
        self.assertTrue(first["pinned"])
        # .. but that the second is before the first
        self.assertGreater(first["startTime"], second["startTime"])
