from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.app.events.serializers import EventCreateAndUpdateSerializer
from lego.users.models import AbakusGroup, User

_test_event_data = {
    'title': 'Event',
    'author': 1,
    'ingress': 'TestIngress',
    'text': 'TestText',
    'event_type': 4,
    'location': 'F252',
    'start_time': '2011-09-01T13:20:30+03:00',
    'end_time': '2012-09-01T13:20:30+03:00',
    'merge_time': '2012-01-01T13:20:30+03:00',
    'pools':
        [
            {
                'name': 'TESTPOOL1',
                'capacity': 10,
                'activation_date': '2012-09-01T13:20:30+03:00'
            },
            {
                'name': 'TESTPOOL2',
                'capacity': 20,
                'activation_date': '2012-09-02T13:20:30+03:00'
            }
        ]

}


def _get_list_url():
    return reverse('api:v1:event-list')


def _get_detail_url(pk):
    return reverse('api:v1:event-detail', kwargs={'pk': pk})


class ListEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

        self.abakus_group = AbakusGroup.objects.get(name='Abakus')
        self.webkom_group = AbakusGroup.objects.get(name='Webkom')

    def test_with_abakus_user(self):
        self.abakus_group.add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_with_webkom_user(self):
        self.webkom_group.add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)


class RetrieveEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.filter(is_superuser=False).first()
        self.abakus_group = AbakusGroup.objects.get(name='Abakus')
        self.abakus_group.add_user(self.abakus_user)

    def test_with_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(1))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(2))
        self.assertEqual(response.status_code, 404)


class CreateEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.filter(is_superuser=False).first()
        self.event_admin_test = AbakusGroup.objects.get(name='EventAdminTest')
        self.event_admin_test.add_user(self.abakus_user)

    def test_create(self):
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(_get_list_url(), _test_event_data)
        test = EventCreateAndUpdateSerializer(data=_test_event_data)
        if not test.is_valid():
            print(test.errors)
        self.assertEqual(response.status_code, 201)
