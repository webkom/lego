from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from lego.apps.events.constants import INTEREST_EVENT
from lego.apps.events.models import Event
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
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        events = res.json()["events"]
        self.assertGreater(len(events), 1)
        first = events[0]
        second = events[1]
        # Check that the first event is pinned
        self.assertTrue(first["pinned"])
        # .. but that the second is before the first
        self.assertGreater(first["startTime"], second["startTime"])

    def test_pinned_is_first_not_logged_in(self):
        res = self.client.get(_get_frontpage())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        events = res.json()["events"]
        self.assertGreater(len(events), 1)
        first = events[0]
        second = events[1]
        # Check that the first event is pinned
        self.assertTrue(first["pinned"])
        # .. but that the second is before the first
        self.assertGreater(first["startTime"], second["startTime"])

    def test_interest_events_are_excluded(self):
        """Interest events have their own page and stay off the frontpage"""
        event = Event.objects.filter(end_time__gt=timezone.now()).first()
        self.assertIsNotNone(event)
        Event.objects.filter(id=event.id).update(event_type=INTEREST_EVENT)

        self.client.force_authenticate(self.user)
        res = self.client.get(_get_frontpage())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(event.id, [e["id"] for e in res.json()["events"]])
