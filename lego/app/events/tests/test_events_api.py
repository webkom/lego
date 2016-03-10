from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.app.events.models import Event
from lego.users.models import AbakusGroup, User

_test_event_data = [
    {
        'title': 'Event1',
        'author': 1,
        'description': 'Ingress1',
        'text': 'Ingress1',
        'event_type': 4,
        'location': 'F252',
        'start_time': '2011-09-01T13:20:30Z',
        'end_time': '2012-09-01T13:20:30Z',
        'merge_time': '2012-01-01T13:20:30Z'
    },
    {
        'title': 'Event2',
        'author': 1,
        'description': 'Ingress2',
        'text': 'Ingress2',
        'event_type': 4,
        'location': 'F252',
        'start_time': '2015-09-01T13:20:30Z',
        'end_time': '2015-09-01T13:20:30Z',
        'merge_time': '2016-01-01T13:20:30Z'
    }
]

_test_pools_data = [
    {
        'name': 'TESTPOOL1',
        'capacity': 10,
        'activation_date': '2012-09-01T10:20:30Z',
        'permission_groups': [1]
    },
    {
        'name': 'TESTPOOL2',
        'capacity': 20,
        'activation_date': '2012-09-02T11:20:30Z',
        'permission_groups': [10]
    },
    {
        'name': 'TESTPOOL3',
        'capacity': 30,
        'activation_date': '2012-09-02T12:20:30Z',
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
    return reverse('api:v1:pool-list', kwargs={'event_pk': event_pk})


def _get_pools_detail_url(event_pk, pool_pk):
    return reverse('api:v1:pool-detail', kwargs={'event_pk': event_pk,
                                                 'pk': pool_pk})


def _get_register_list_url(event_pk):
    return reverse('api:v1:register-list', kwargs={'event_pk': event_pk})


class ListEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.data), 3)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.data), 4)


class RetrieveEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(2))
        self.assertEqual(event_response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(2))
        self.assertEqual(event_response.status_code, 404)


class CreateEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.event_response = self.client.post(_get_list_url(), _test_event_data[0])
        self.event_id = self.event_response.data.pop('id', None)
        self.pool_response = self.client.post(_get_pools_list_url(self.event_id),
                                              _test_pools_data[0])
        self.pool_id = self.pool_response.data.get('id', None)

    def test_event_creation(self):
        self.assertIsNotNone(self.event_id)
        self.assertEqual(self.event_response.status_code, 201)
        self.assertEqual(_test_event_data[0], self.event_response.data)

    def test_event_update(self):
        event_update_response = self.client.put(_get_detail_url(self.event_id), _test_event_data[1])

        self.assertEqual(self.event_id, event_update_response.data.pop('id'))
        self.assertEqual(event_update_response.status_code, 200)
        self.assertNotEqual(_test_event_data[0], event_update_response.data)
        self.assertEqual(_test_event_data[1], event_update_response.data)

    def test_pool_creation(self):
        self.assertIsNotNone(self.pool_response.data.pop('id'))
        self.assertEqual(self.pool_response.status_code, 201)
        self.assertEqual(_test_pools_data[0], self.pool_response.data)

    def test_pool_update(self):
        pool_update_response = self.client.put(_get_pools_detail_url(self.event_id, self.pool_id),
                                               _test_pools_data[1])
        pool_get_response = self.client.get(_get_pools_detail_url(self.event_id, self.pool_id))
        pool_get_response.data.pop('registrations')  # The put does not return updated data

        self.assertEqual(pool_update_response.status_code, 200)
        self.assertIsNotNone(pool_get_response.data.pop('id'))
        self.assertEqual(_test_pools_data[1], pool_get_response.data)


class RetrievePoolsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 403)


class CreateRegistrationsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

    def test_create(self):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_register_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 201)

    def test_register_no_pools(self):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        registration_response = self.client.post(_get_register_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 400)


class ListRegistrationsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(1))
        self.assertEqual(event_response.status_code, 200)

        registrations_exist = False
        for pool in event_response.data.get('pools', None):
            if pool.get('registrations', None):
                registrations_exist = True
        self.assertTrue(registrations_exist)

    def test_without_group_permission(self):
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(1))

        self.assertEqual(event_response.status_code, 404)
