from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.app.events.serializers import (EventCreateAndUpdateSerializer,
                                         RegistrationCreateAndUpdateSerializer)
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
}

_test_pools_data = [
    {
        'name': 'TESTPOOL1',
        'capacity': 10,
        'activation_date': '2012-09-01T13:20:30+03:00',
        'permission_groups': [1]
    },
    {
        'name': 'TESTPOOL2',
        'capacity': 20,
        'activation_date': '2012-09-02T13:20:30+03:00',
        'permission_groups': [10]
    },
    {
        'name': 'TESTPOOL3',
        'capacity': 30,
        'activation_date': '2012-09-02T13:20:30+03:00',
        'permission_groups': [1]
    }
]

_test_registration_data = {
    'user': 1,
}


def _get_list_url():
    return reverse('api:v1:event-list')


def _get_detail_url(pk):
    return reverse('api:v1:event-detail', kwargs={'pk': pk})


def _get_pools_list_url(event_pk):
    return reverse('pool-list', kwargs={'event_pk': event_pk})


def _get_pools_detail_url(event_pk, pool_pk):
    return reverse('pool-detail', kwargs={'event_pk': event_pk,
                                          'pk': pool_pk})


def _get_register_list_url(event_pk):
    return reverse('register-list', kwargs={'event_pk': event_pk})


def _get_registration_list_url(event_pk, pool_pk):
    return reverse('registration-list', kwargs={'event_pk': event_pk,
                                                'pool_pk': pool_pk})


def _get_registration_detail_url(event_pk, pool_pk, registration_pk):
    return reverse('registration-detail', kwargs={'event_pk': event_pk,
                                                  'pool_pk': pool_pk,
                                                  'pk': registration_pk})


class ListEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)


class RetrieveEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(2))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_detail_url(2))
        self.assertEqual(response.status_code, 404)


class CreateEventsTestCase(APITestCase):
    fixtures = ['test_users.yaml', 'initial_abakus_groups.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)

    def test_create(self):
        self.client.force_authenticate(self.abakus_user)
        response = self.client.post(_get_list_url(), _test_event_data)
        test = EventCreateAndUpdateSerializer(data=_test_event_data)
        if not test.is_valid():
            print(test.errors)
        self.assertEqual(response.status_code, 201)

    def test_pool_creation(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.post(_get_list_url(), _test_event_data)
        self.assertEqual(response.status_code, 201)

        pool_response = self.client.post(_get_pools_list_url(response.data['id']),
                                         _test_pools_data[0])
        self.assertIsNotNone(pool_response.data.pop('id'))
        self.assertEqual(pool_response.status_code, 201)
        self.assertEqual(_test_pools_data[0], pool_response.data)


class RetrievePoolsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(response.status_code, 403)


class CreateRegistrationsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)

    def test_create(self):
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.post(_get_list_url(), _test_event_data)
        event_id = event_response.data['id']

        self.client.post(_get_pools_list_url(event_response.data['id']), _test_pools_data[0])

        test = RegistrationCreateAndUpdateSerializer(data=_test_registration_data)
        if not test.is_valid():
            print(test.errors)

        registration_response = self.client.post(_get_register_list_url(event_id), {})
        self.assertEqual(registration_response.status_code, 201)

    def test_admin_create(self):
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.post(_get_list_url(), _test_event_data)
        event_id = event_response.data['id']

        pool_response = self.client.post(_get_pools_list_url(event_id),
                                         _test_pools_data[0])
        pool_id = pool_response.data['id']

        test = RegistrationCreateAndUpdateSerializer(data=_test_registration_data)
        if not test.is_valid():
            print(test.errors)

        registration_response = self.client.post(_get_registration_list_url(event_id, pool_id),
                                                 _test_registration_data)
        self.assertEqual(registration_response.status_code, 201)


class RetrieveRegistrationsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_registration_detail_url(1, 1, 1))
        self.assertEqual(response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_registration_detail_url(1, 1, 1))
        self.assertEqual(response.status_code, 403)


class ListRegistrationsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_registration_list_url(1, 1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_without_group_permission(self):
        self.client.force_authenticate(user=self.abakus_user)
        response = self.client.get(_get_registration_list_url(1, 1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
