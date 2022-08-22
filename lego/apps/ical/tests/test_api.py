import re
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from icalendar import Calendar

from lego.apps.events.models import Event, Pool
from lego.apps.ical.models import ICalToken
from lego.apps.meetings.models import Meeting
from lego.apps.permissions.constants import VIEW
from lego.apps.users.models import AbakusGroup, User
from lego.utils.test_utils import BaseAPITestCase


def _get_token_url():
    return reverse("api:v1:calendar-token-list")


def _get_token_regenerate_url():
    return reverse("api:v1:calendar-token-regenerate")


def _get_ical_list_url(token):
    return reverse("api:v1:calendar-ical-list") + f"?token={token}"


def _get_ical_events_url(token):
    return reverse("api:v1:calendar-ical-events") + f"?token={token}"


def _get_ical_personal_url(token):
    return reverse("api:v1:calendar-ical-personal") + f"?token={token}"


def _get_ical_registrations_url(token):
    return reverse("api:v1:calendar-ical-registrations") + f"?token={token}"


def _get_all_ical_urls(token):
    return [
        _get_ical_events_url(token),
        _get_ical_registrations_url(token),
        _get_ical_personal_url(token),
    ]


def _get_ical_event_meta(ical_event):
    """
    Splits the 'UID' tag on the format:
    "event-12@abakus.no", into
    ["event", 12, "abakus.no"]

    usage:

    eventType, pk, domain = _get_ical_event_meta(ical_event)
    """
    return re.split("-|@", ical_event["UID"])


def _get_ical(url, client):
    res = client.get(url)
    return Calendar.from_ical(res.content)


def _get_ical_events(url, client):
    return _get_ical(url, client).subcomponents


class IcalAuthenticationTestCase(BaseAPITestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_events.yaml",
        "test_meetings.yaml",
        "test_companies.yaml",
        "test_followevent.yaml",
    ]

    def setUp(self):
        Event.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            end_time=timezone.now() + timedelta(hours=4),
        )
        Pool.objects.all().update(activation_date=timezone.now() + timedelta(hours=1))
        Meeting.objects.all().update(
            start_time=timezone.now() + timedelta(hours=3),
            end_time=timezone.now() + timedelta(hours=4),
        )

        self.meeting = Meeting.objects.get(id=1)
        self.user = User.objects.get(username="abakule")
        self.meeting.invite_user(self.user)
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        self.token = ICalToken.objects.get_or_create(user=self.user)[0].token

    def help_test_ical_content_permission(self, ical_content, user):
        """
        Tests that permissions are ok.

        Tests that the user can view every
        event/meeting in the ical result.

        """
        icalendar = Calendar.from_ical(ical_content)
        for event in icalendar.subcomponents:
            eventType, pk, domain = _get_ical_event_meta(event)
            if eventType == "event":
                self.assertTrue(user.has_perm(VIEW, Event.objects.get(id=pk)))
            elif eventType == "meeting":
                self.assertTrue(user.has_perm(VIEW, Meeting.objects.get(id=pk)))

    def test_get_list(self, *args):
        res = self.client.get(_get_ical_list_url(self.token))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_token = res.json()["result"]["token"]["token"]
        self.assertEqual(res_token, self.token)

        res = self.client.get(_get_ical_list_url(self.token))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_with_token(self, *args):
        for url in _get_all_ical_urls(self.token):
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.help_test_ical_content_permission(res.content, self.user)

    def test_get_ical_authenticated(self, *args):
        self.client.force_authenticate(self.user)
        for url in _get_all_ical_urls(""):
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.help_test_ical_content_permission(res.content, self.user)

    def test_get_ical_without_authentication(self, *args):
        for url in _get_all_ical_urls(""):
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_ical_with_invalid_token(self, *args):
        for url in _get_all_ical_urls("invalid-token-here"):
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class IcalPersonalTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        self.token = ICalToken.objects.get_or_create(user=self.user)[0].token
        self.url = _get_ical_personal_url(self.token)

    def test_empty_calendar(self):
        ical_events = _get_ical_events(self.url, self.client)
        self.assertEqual(len(ical_events), 0)

    def test_meeting_invitation(self):
        meeting = Meeting.objects.create(
            title="testing",
            report="TBA",
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=4),
        )
        ical_events = _get_ical_events(self.url, self.client)
        self.assertEqual(len(ical_events), 0)

        meeting.invite_user(self.user)

        ical_events = _get_ical_events(self.url, self.client)
        self.assertEqual(len(ical_events), 1)

        eventType, pk, domain = _get_ical_event_meta(ical_events[0])
        self.assertEqual(int(pk), meeting.pk)


class IcalEventsTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(username="test1")
        AbakusGroup.objects.get(name="Abakus").add_user(self.user)
        self.token = ICalToken.objects.get_or_create(user=self.user)[0].token
        self.events_url = _get_ical_events_url(self.token)
        self.registrations_url = _get_ical_registrations_url(self.token)
        abakom_group = AbakusGroup.objects.get(name="Abakom")
        self.event = Event.objects.create(
            title="AbakomEvent",
            event_type=0,
            start_time=timezone.now() + timedelta(hours=7),
            end_time=timezone.now() + timedelta(hours=10),
            require_auth=True,
        )
        self.event.can_view_groups.add(abakom_group)
        self.event.save()
        self.pool = Pool.objects.create(
            name="Webkom",
            capacity=1,
            event=self.event,
            activation_date=(timezone.now() + timedelta(hours=3)),
        )
        self.pool.permission_groups.add(abakom_group)
        self.pool.save()

    def test_non_abakom_user(self):
        for url in [self.events_url, self.registrations_url]:
            ical_events = _get_ical_events(url, self.client)
            self.assertEqual(len(ical_events), 0)

    def test_public_event_can_register(self):
        self.event.require_auth = False
        self.event.save()
        self.pool.permission_groups.add(AbakusGroup.objects.get(name="Abakus"))
        for url in [self.events_url, self.registrations_url]:

            ical_events = _get_ical_events(url, self.client)
            self.assertEqual(len(ical_events), 1)

            eventType, pk, domain = _get_ical_event_meta(ical_events[0])
            self.assertEqual(int(pk), self.event.pk)

    def test_public_event_can_view_not_register(self):
        self.event.require_auth = False
        self.event.save()

        ical_events = _get_ical_events(self.events_url, self.client)
        self.assertEqual(len(ical_events), 1)

        eventType, pk, domain = _get_ical_event_meta(ical_events[0])
        self.assertEqual(int(pk), self.event.pk)

        ical_events = _get_ical_events(self.registrations_url, self.client)
        self.assertEqual(len(ical_events), 0)

    def test_abakom_user(self):
        AbakusGroup.objects.get(name="Abakom").add_user(self.user)
        for url in [self.events_url, self.registrations_url]:
            ical_events = _get_ical_events(url, self.client)
            self.assertEqual(len(ical_events), 1)

            eventType, pk, domain = _get_ical_event_meta(ical_events[0])
            self.assertEqual(int(pk), self.event.pk)


class ICalTokenGenerateTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakommer = User.objects.get(username="abakommer")

    def test_get_token_initial(self):
        self.client.force_authenticate(self.abakommer)

        res = self.client.get(_get_token_url())
        token = ICalToken.objects.get(user=self.abakommer)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["token"], token.token)


class ICalTokenRegenerateTestCase(BaseAPITestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    def setUp(self):
        self.abakommer = User.objects.get(username="abakommer")
        self.token = ICalToken.objects.create(user=self.abakommer)

    def test_regenerate_token(self):
        self.client.force_authenticate(self.abakommer)

        old_token = ICalToken.objects.get(user=self.abakommer).token
        res = self.client.patch(_get_token_regenerate_url())
        new_token = ICalToken.objects.get(user=self.abakommer).token

        self.assertNotEqual(old_token, new_token)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["token"], new_token)
        self.assertNotEqual(res.json()["token"], old_token)

    def test_not_regenerate_token(self):
        self.client.force_authenticate(self.abakommer)

        old_token = ICalToken.objects.get(user=self.abakommer).token
        res = self.client.get(_get_token_url())
        new_token = ICalToken.objects.get(user=self.abakommer).token

        self.assertEqual(old_token, new_token)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["token"], new_token)
        self.assertEqual(res.json()["token"], old_token)
