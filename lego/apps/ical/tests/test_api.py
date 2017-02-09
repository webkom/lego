from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.meetings.models import Meeting
from lego.apps.users.models import AbakusGroup, User

from lego.apps.ical.models import ICalToken


def _get_token_url():
    return reverse('api:v1:calendar-token-list')


def _get_token_regenerate_url():
    return reverse('api:v1:calendar-token-regenerate')


def _get_ical_list_url():
    return reverse('api:v1:calendar-ical-list') + f'?token={token}'


def _get_ical_meetings_url(token):
    return reverse('api:v1:calendar-ical-meetings') + f'?token={token}'


def _get_ical_events_url(token):
    return reverse('api:v1:calendar-ical-events') + f'?token={token}'


def _get_ical_favorites_url(token):
    return reverse('api:v1:calendar-ical-favorites') + f'?token={token}'


def _get_ical_registrations_url(token):
    return reverse('api:v1:calendar-ical-registrations') + f'?token={token}'


def _get_all_ical_urls():
    return [
        _get_ical_events_url,
        _get_ical_favorites_url,
        _get_ical_registrations_url,
        _get_ical_meetings_url
    ]


class RetreiveICalTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_meetings.yaml', 'test_users.yaml']

    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.meeting2 = Meeting.objects.get(id=2)
        self.abakommer = User.objects.get(username='abakommer')
        AbakusGroup.objects.get(name='Abakom').add_user(self.abakommer)
        self.abakule = User.objects.get(username='test1')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakule)
        self.pleb = User.objects.get(username='pleb')
        self.token = ICalToken.objects.get_or_create(user=self.abakommer)[0].token

    def test_get_ical_events_token(self):
        res = self.client.get(_get_ical_events_url(self.token))
        self.assertEqual(res.status_code, 200)

    def test_get_ical_meetings_token(self):
        res = self.client.get(_get_ical_meetings_url(self.token))
        self.assertEqual(res.status_code, 200)

    def test_get_ical_favorites_token(self):
        res = self.client.get(_get_ical_favorites_url(self.token))
        self.assertEqual(res.status_code, 200)

    def test_get_ical_registrations_token(self):
        res = self.client.get(_get_ical_registrations_url(self.token))
        self.assertEqual(res.status_code, 200)

    def test_get_without_token(self):
        for func in _get_all_ical_urls():
            res = self.client.get(func(''))
            self.assertEqual(res.status_code, 401)

    def test_as_auth_as_user(self):
        self.client.force_authenticate(self.abakommer)
        for func in _get_all_ical_urls():
            res = self.client.get(func(''))
            self.assertEqual(res.status_code, 200)


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

    def test_not_regenerate_token(self):
        self.client.force_authenticate(self.abakommer)

        old_token = ICalToken.objects.get(user=self.abakommer).token
        res = self.client.get(_get_token_url())
        new_token = ICalToken.objects.get(user=self.abakommer).token

        self.assertEqual(old_token, new_token)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['token'], new_token)
        self.assertEqual(res.data['token'], old_token)
