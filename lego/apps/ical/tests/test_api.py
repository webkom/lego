import re
from unittest import mock

from django.core.urlresolvers import reverse
from django.utils import timezone
from icalendar import Calendar
from rest_framework.test import APITestCase

from lego.apps.events.models import Event
from lego.apps.ical.models import ICalToken
from lego.apps.meetings.models import Meeting
from lego.apps.users.models import AbakusGroup, User


def _get_token_url():
    return reverse('api:v1:calendar-token-list')


def _get_token_regenerate_url():
    return reverse('api:v1:calendar-token-regenerate')


def _get_ical_list_url(token):
    return reverse('api:v1:calendar-ical-list') + f'?token={token}'


def _get_ical_events_url(token):
    return reverse('api:v1:calendar-ical-events') + f'?token={token}'


def _get_ical_personal_url(token):
    return reverse('api:v1:calendar-ical-personal') + f'?token={token}'


def _get_ical_registrations_url(token):
    return reverse('api:v1:calendar-ical-registrations') + f'?token={token}'


def _get_all_ical_urls(token):
    return [
        _get_ical_events_url(token),
        _get_ical_registrations_url(token),
        _get_ical_personal_url(token)
    ]


NOW_FOR_TESTING = timezone.make_aware(
    timezone.datetime(2009, 1, 1, 1),
    timezone.get_current_timezone()
)


@mock.patch('django.utils.timezone.now', side_effect=lambda: NOW_FOR_TESTING)
class RetreiveDateDependentICalTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_meetings.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_followevent.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.user = User.objects.get(username='abakule')
        self.meeting.invite_user(self.user)
        AbakusGroup.objects.get(name='Abakus').add_user(self.user)
        AbakusGroup.objects.get(name='Abakom').add_user(self.user)
        self.token = ICalToken.objects.get_or_create(user=self.user)[0].token

    def help_test_ical_content_permission(self, ical_content, user):
        """
        Tests that permissions are ok.

        Tests that the user can view every
        event/meeting in the ical result.

        Splits the 'UID' tag on the format:
        "event-12@abakus.no", into
        ["event", 12, "abakus.no"]
        """
        icalendar = Calendar.from_ical(ical_content)
        for event in icalendar.subcomponents:
            hits = re.split("-|@", event['UID'])
            if hits[0] == "event":
                self.assertTrue(Event.objects.get(id=hits[1]).can_view(user))
            elif hits[0] == "meeting":
                self.assertTrue(Meeting.objects.get(id=hits[1]).can_edit(user))

    def test_get_list(self, *args):
        res = self.client.get(_get_ical_list_url(self.token))
        self.assertEqual(res.status_code, 200)
        res_token = res.data['result']['token']['token']
        self.assertEqual(res_token, self.token)

        res = self.client.get(_get_ical_list_url(self.token))
        self.assertEqual(res.status_code, 200)

    def test_get_with_token(self, *args):
        for url in _get_all_ical_urls(self.token):
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)
            self.help_test_ical_content_permission(res.content, self.user)

    def test_get_ical_authenticated(self, *args):
        self.client.force_authenticate(self.user)
        for url in _get_all_ical_urls(self.token):
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)
            self.help_test_ical_content_permission(res.content, self.user)
        self.client.force_authenticate(user=None)

    def test_get_ical_without_authentication(self, *args):
        for url in _get_all_ical_urls(''):
            res = self.client.get(url)
            self.assertEqual(res.status_code, 401)

    def test_get_ical_with_invalid_token(self, *args):
        for url in _get_all_ical_urls('invalid-token-here'):
            res = self.client.get(url)
            self.assertEqual(res.status_code, 401)


@mock.patch('django.utils.timezone.now', side_effect=lambda: NOW_FOR_TESTING)
class RetreiveDateDependentICalTestCaseUser(RetreiveDateDependentICalTestCase):
    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.user = User.objects.get(username='pleb')
        self.meeting.invite_user(self.user)
        self.token = ICalToken.objects.get_or_create(user=self.user)[0].token


@mock.patch('django.utils.timezone.now', side_effect=lambda: NOW_FOR_TESTING)
class RetreiveDateDependentICalTestCaseWebkom(RetreiveDateDependentICalTestCase):
    def setUp(self):
        self.user = User.objects.get(pk=1)
        AbakusGroup.objects.get(pk=11).add_user(self.user)
        self.token = ICalToken.objects.get_or_create(user=self.user)[0].token


class ICalTokenGenerateTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.abakommer = User.objects.get(username='abakommer')

    def test_get_token_initial(self):
        self.client.force_authenticate(self.abakommer)

        res = self.client.get(_get_token_url())
        token = ICalToken.objects.get(user=self.abakommer)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['token'], token.token)


class ICalTokenRegenerateTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.abakommer = User.objects.get(username='abakommer')
        self.token = ICalToken.objects.create(user=self.abakommer)

    def test_regenerate_token(self):
        self.client.force_authenticate(self.abakommer)

        old_token = ICalToken.objects.get(user=self.abakommer).token
        res = self.client.get(_get_token_regenerate_url())
        new_token = ICalToken.objects.get(user=self.abakommer).token

        self.assertNotEqual(old_token, new_token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['token'], new_token)
        self.assertNotEqual(res.data['token'], old_token)
        self.client.force_authenticate(user=None)

    def test_not_regenerate_token(self):
        self.client.force_authenticate(self.abakommer)

        old_token = ICalToken.objects.get(user=self.abakommer).token
        res = self.client.get(_get_token_url())
        new_token = ICalToken.objects.get(user=self.abakommer).token

        self.assertEqual(old_token, new_token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['token'], new_token)
        self.assertEqual(res.data['token'], old_token)
        self.client.force_authenticate(user=None)
