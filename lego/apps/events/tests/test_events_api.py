from copy import deepcopy
from datetime import timedelta
from unittest import mock, skipIf

import stripe
from django.core.urlresolvers import reverse
from django.utils import timezone
from djangorestframework_camel_case.render import camelize
from rest_framework.test import APITestCase, APITransactionTestCase

from lego.apps.events import constants
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tasks import stripe_webhook_event
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.models import AbakusGroup, User

from .utils import create_token

_test_event_data = [
    {
        'title': 'Event1',
        'description': 'Ingress1',
        'text': 'Ingress1',
        'event_type': 'event',
        'location': 'F252',
        'start_time': '2011-09-01T13:20:30Z',
        'end_time': '2012-09-01T13:20:30Z',
        'merge_time': '2012-01-01T13:20:30Z',
        'pools': [{
            'name': 'Initial Pool',
            'capacity': 10,
            'activation_date': '2012-09-01T10:20:30Z',
            'permission_groups': [1]
        }]
    },
    {
        'title': 'Event2',
        'description': 'Ingress2',
        'text': 'Ingress2',
        'event_type': 'event',
        'location': 'F252',
        'start_time': '2015-09-01T13:20:30Z',
        'end_time': '2015-09-01T13:20:30Z',
        'merge_time': '2016-01-01T13:20:30Z',
        'pools': [{
            'name': 'Initial Pool 1',
            'capacity': 10,
            'activation_date': '2012-09-01T10:20:30Z',
            'permission_groups': [2]
        }, {
            'name': 'Initial Pool 2',
            'capacity': 20,
            'activation_date': '2012-09-01T10:20:30Z',
            'permission_groups': [2]
        }]
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


def _get_registrations_list_url(event_pk):
    return reverse('api:v1:registrations-list', kwargs={'event_pk': event_pk})


def _get_registrations_detail_url(event_pk, registration_pk):
    return reverse('api:v1:registrations-detail', kwargs={'event_pk': event_pk,
                                                          'pk': registration_pk})


class ListEventsTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        date = timezone.now().replace(hour=16, minute=15, second=0, microsecond=0)
        for event in Event.objects.all():
            event.start_time = date + timedelta(days=10)
            event.end_time = date + timedelta(days=10, hours=4)
            event.save()

    def test_with_abakus_user(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.data['results']), 4)

    def test_with_webkom_user(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_list_url())
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(len(event_response.data['results']), 5)


class RetrieveEventsTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        """Test that abakus user can retrieve event"""
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(2))
        self.assertEqual(event_response.status_code, 200)

    def test_without_group_permission(self):
        """Test that plain user cannot retrieve event"""
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(2))
        self.assertEqual(event_response.status_code, 404)

    def test_without_group_permission_webkom_only(self):
        """Test that abakus user cannot retrieve webkom only event"""
        event = Event.objects.get(title='NO_POOLS_WEBKOM')
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(event.id))
        self.assertEqual(event_response.status_code, 404)

    def test_charge_status_hidden_when_not_priced(self):
        """Test that chargeStatus is hidden when getting nonpriced event"""
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(1))

        for pool in event_response.data['pools']:
            for reg in pool['registrations']:
                with self.assertRaises(KeyError):
                    reg['chargeStatus']

    def test_only_own_fields_visible(self):
        """Test that a user can only view own fields"""
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(_get_detail_url(5))

        for pool in event_response.data['pools']:
            for reg in pool['registrations']:
                if reg['user']['id'] == self.abakus_user.id:
                    self.assertIsNotNone(reg['feedback'])
                    self.assertIsNotNone(reg['chargeStatus'])
                else:
                    self.assertIsNone(reg['feedback'])
                    self.assertIsNone(reg['chargeStatus'])


class CreateEventsTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.event_response = self.client.post(_get_list_url(), _test_event_data[0])
        self.assertEqual(self.event_response.status_code, 201)
        self.event_id = self.event_response.data.pop('id', None)

    def test_event_creation(self):
        """Test event creation with pools"""
        self.assertIsNotNone(self.event_id)
        self.assertEqual(self.event_response.status_code, 201)
        res_event = self.event_response.data
        expect_event = _test_event_data[0]
        for key in ['title', 'description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

        expect_pools = camelize(expect_event['pools'])
        res_pools = res_event['pools']
        for i in range(len(expect_pools)):
            self.assertIsNotNone(res_pools[i].pop('id'))
            for key in ['name', 'capacity', 'activationDate', 'permissionGroups']:
                self.assertEqual(res_pools[i][key], expect_pools[i][key])

    def test_event_creation_without_perm(self):
        user = User.objects.get(username='abakule')
        self.client.force_authenticate(user)
        response = self.client.post(_get_list_url(), _test_event_data[1])
        self.assertEqual(response.status_code, 403)

    def test_event_update(self):
        """Test updating event attributes"""
        expect_event = _test_event_data[1]
        expect_event.pop('pools')
        event_update_response = self.client.put(_get_detail_url(self.event_id), expect_event)
        self.assertEqual(event_update_response.status_code, 200)
        self.assertEqual(self.event_id, event_update_response.data.pop('id'))
        res_event = event_update_response.data
        for key in ['title', 'description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

    def test_event_partial_update(self):
        """Test patching event attributes"""
        expect_event = _test_event_data[0]
        event_update_response = self.client.patch(
            _get_detail_url(self.event_id), {'title': 'PATCHED'}
        )
        self.assertEqual(event_update_response.status_code, 200)
        self.assertEqual(self.event_id, event_update_response.data.pop('id'))
        res_event = event_update_response.data
        self.assertEqual(res_event['title'], 'PATCHED')
        for key in ['description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

    def test_event_update_with_pool_creation(self):
        """Test updating event attributes and add a pool"""
        expect_event = _test_event_data[1]
        expect_event['pools'] = self.event_response.data.get('pools') + [_test_pools_data[0]]
        event_update_response = self.client.put(_get_detail_url(self.event_id), expect_event)
        self.assertEqual(event_update_response.status_code, 200)
        self.assertEqual(self.event_id, event_update_response.data.pop('id'))
        res_event = event_update_response.data
        for key in ['title', 'description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

        # These are not sorted due to id not present on new pool
        # camelize() because nested serializer (pool) camelizes output
        expect_pools = sorted(camelize(expect_event['pools']), key=lambda pool: pool['name'])
        res_pools = sorted(res_event['pools'], key=lambda pool: pool['name'])
        for i in range(len(expect_pools)):
            self.assertIsNotNone(res_pools[i].pop('id'))
            for key in ['name', 'capacity', 'activationDate', 'permissionGroups']:
                self.assertEqual(res_pools[i][key], expect_pools[i][key])

    def test_event_update_with_pool_deletion(self):
        """Test that pool updated through event is deleted"""
        _test_event_data[1]['pools'] = [_test_pools_data[0]]
        event_update_response = self.client.put(_get_detail_url(self.event_id), _test_event_data[1])

        self.assertEqual(event_update_response.status_code, 200)
        res_event = event_update_response.data
        expect_event = _test_event_data[1]
        for key in ['title', 'description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

        expect_pools = camelize(expect_event['pools'])
        res_pools = res_event['pools']
        for i in range(len(expect_pools)):
            self.assertIsNotNone(res_pools[i].pop('id'))
            for key in ['name', 'capacity', 'activationDate', 'permissionGroups']:
                self.assertEqual(res_pools[i][key], expect_pools[i][key])

    def test_event_partial_update_pool_deletion(self):
        """Test that all pools are deleted when patching"""
        event_update_response = self.client.patch(_get_detail_url(self.event_id), {'pools': []})

        self.assertEqual(event_update_response.status_code, 200)
        res_event = event_update_response.data
        expect_event = _test_event_data[0]
        for key in ['title', 'description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

        self.assertEqual(res_event['pools'], [])


class PoolsTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_create_pool(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.post(_get_pools_list_url(1), _test_pools_data[0])
        self.assertEqual(pool_response.status_code, 201)

    def test_create_pool_as_bedkom(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.post(_get_pools_list_url(1), _test_pools_data[0])
        self.assertEqual(pool_response.status_code, 201)

    def test_create_failing_pool_as_abakus(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.post(_get_pools_list_url(1), _test_pools_data[0])
        self.assertEqual(pool_response.status_code, 403)

    def test_delete_pool_with_registrations_as_admin(self):
        """Test that pool deletion is not possible when registrations are attached"""
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.delete(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 409)

    def test_delete_pool_without_registrations_as_admin(self):
        """Test that pool deletion is possible without attached registrations"""
        pool = Pool.objects.create(
            name='Testpool', event_id=1, activation_date=timezone.now()
        )
        pool.permission_groups.set([1, 2])
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.delete(_get_pools_detail_url(1, pool.id))
        self.assertEqual(pool_response.status_code, 204)

    def test_delete_pool_without_registrations_as_abakus(self):
        """Test that abakususer cannot delete pool"""
        pool = Pool.objects.create(
            name='Testpool', event_id=1, activation_date=timezone.now()
        )
        pool.permission_groups.set([1, 2])
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.delete(_get_pools_detail_url(1, pool.id))
        self.assertEqual(pool_response.status_code, 403)


@mock.patch('lego.apps.events.views.verify_captcha', return_value=True)
class RegistrationsTransactionTestCase(APITransactionTestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

    def test_create(self, *args):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(registration_response.data.get('status'), constants.PENDING_REGISTER)
        res = self.client.get(_get_registrations_detail_url(
            event.id, registration_response.data['id'])
        )
        self.assertEqual(res.data['user']['id'], 1)
        self.assertEqual(res.data['status'], constants.SUCCESS_REGISTER)

    def test_register_no_pools(self, *args):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(registration_response.data.get('status'), constants.PENDING_REGISTER)
        res = self.client.get(
            _get_registrations_detail_url(event.id, registration_response.data['id'])
        )
        self.assertEqual(res.data['status'], constants.FAILURE_REGISTER)

    def test_unregister(self, *args):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        registration = Registration.objects.get(user=self.abakus_user, event=event)
        registration_response = self.client.delete(
            _get_registrations_detail_url(event.id, registration.id)
        )

        get_unregistered = self.client.get(_get_registrations_detail_url(event.id, registration.id))
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(get_unregistered.status_code, 200)
        self.assertIsNone(get_unregistered.data.get('pool'))


@mock.patch('lego.apps.events.views.verify_captcha', return_value=True)
class RegistrationsTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

    def test_unable_to_create(self, *args):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.non_abakus_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name='Users').add_user(self.non_abakus_user)
        self.client.force_authenticate(self.non_abakus_user)
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 403)

    def test_update_feedback(self, *args):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'feedback': 'UPDATED'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['feedback'], 'UPDATED')

    def test_update_presence_without_permission(self, *args):
        """ Test that abakus user cannot update presence """
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'presence': 'PRESENT'}
        )
        self.assertEqual(res.status_code, 403)

    def test_update_presence_with_permission(self, *args):
        """ Test that admin can update presence """
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'presence': 'PRESENT'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['presence'], 'PRESENT')

    def test_user_cannot_update_other_registration(self, *args):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})

        self.other_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name='Abakus').add_user(self.other_user)
        self.client.force_authenticate(self.other_user)
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'feedback': 'UPDATED'}
        )
        self.assertEqual(res.status_code, 403)

    def test_admin_update_registration(self, *args):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})

        self.webkom_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name='Webkom').add_user(self.webkom_user)
        self.client.force_authenticate(self.webkom_user)
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'feedback': 'UPDATED_BY_ADMIN'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['feedback'], 'UPDATED_BY_ADMIN')

    def test_can_not_unregister_other_user(self, *args):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        registration = Registration.objects.get(user=self.abakus_user, event=event)

        self.other_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name='Abakus').add_user(self.other_user)
        self.client.force_authenticate(self.other_user)
        registration_response = self.client.delete(_get_registrations_detail_url(event.id,
                                                                                 registration.id))

        self.assertEqual(registration_response.status_code, 403)

    def test_required_feedback_failing(self, *args):
        """Test that register returns 400 when not providing feedback when required"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.feedback_required = True
        event.save()
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 400)

    def test_required_feedback_success(self, *args):
        """Test that register returns 202 when providing feedback when required"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.feedback_required = True
        event.save()
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {'feedback': 'TEST'}
        )
        self.assertEqual(registration_response.status_code, 202)

    def test_update_charge_status_with_permissions(self, mock_verify_captcha):
        """Test user with permission can update charge_status"""
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'charge_status': 'manual'}
        )
        self.assertEqual(res.status_code, 200)

    def test_update_charge_status_wrongly_with_permissions(self, mock_verify_captcha):
        """Test user with permission fails in updating charge_status when giving wrong choice"""
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'charge_status': 'feil-data'}
        )
        self.assertEqual(res.status_code, 400)

    def test_update_charge_status_without_permissions(self, mock_verify_captcha):
        """Test that user without permission cannot update charge_status"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'charge_status': 'manual'}
        )
        self.assertEqual(res.status_code, 403)


class EventAdministrateTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)
        self.event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(f'{_get_detail_url(self.event.id)}administrate/')
        self.assertEqual(event_response.status_code, 200)
        self.assertEqual(event_response.data.get('id'), self.event.id)
        self.assertEqual(len(event_response.data.get('pools')), 2)

    def test_without_group_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        event_response = self.client.get(f'{_get_detail_url(self.event.id)}administrate/')
        self.assertEqual(event_response.status_code, 403)


class CreateAdminRegistrationTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_users = User.objects.all()
        self.request_user, self.user = self.abakus_users[0:2]
        self.event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.event.start_time = timezone.now() + timedelta(hours=3)
        self.event.save()
        self.pool = self.event.pools.first()

    def test_with_admin_permission(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.request_user)
        pool_two = self.event.pools.get(name='Webkom')

        self.assertFalse(self.event.can_register(self.user, self.pool))
        self.client.force_authenticate(self.request_user)

        registration_response = self.client.post(
            f'{_get_registrations_list_url(self.event.id)}admin_register/',
            {'user': self.user.id, 'pool': self.pool.id, 'admin_reason': 'test'}
        )

        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(self.pool.registrations.count(), 1)
        self.assertEqual(pool_two.registrations.count(), 0)

    def test_without_admin_permission(self):
        AbakusGroup.objects.get(name='Abakus').add_user(self.user)

        self.assertTrue(self.event.can_register(self.user, self.pool))
        self.client.force_authenticate(self.request_user)

        registration_response = self.client.post(
            f'{_get_registrations_list_url(self.event.id)}admin_register/',
            {'user': self.user.id, 'pool': self.pool.id, 'admin_reason': 'test'}
        )

        self.assertEqual(registration_response.status_code, 403)
        self.assertEqual(self.event.number_of_registrations, 0)

    def test_with_nonexistant_pool(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.request_user)
        AbakusGroup.objects.get(name='Abakus').add_user(self.user)
        nonexistant_pool_id = len(self.event.pools.all())

        self.assertTrue(self.event.can_register(self.user, self.pool))
        self.client.force_authenticate(self.request_user)

        registration_response = self.client.post(
            f'{_get_registrations_list_url(self.event.id)}admin_register/',
            {'user': self.user.id, 'pool': nonexistant_pool_id, 'admin_reason': 'test'}
        )

        self.assertEqual(registration_response.status_code, 400)
        self.assertEqual(self.event.number_of_registrations, 0)

    def test_with_feedback(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.request_user)
        self.client.force_authenticate(self.request_user)
        registration_response = self.client.post(
            f'{_get_registrations_list_url(self.event.id)}admin_register/',
            {'user': self.user.id,
             'pool': self.pool.id,
             'feedback': 'TEST',
             'admin_reason': 'test'
             }
        )

        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(registration_response.data.get('feedback'), 'TEST')

    def test_without_admin_reason(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.request_user)
        self.client.force_authenticate(self.request_user)
        registration_response = self.client.post(
            f'{_get_registrations_list_url(self.event.id)}admin_register/',
            {'user': self.user.id,
             'pool': self.pool.id,
             'feedback': 'TEST',
             'admin_reason': ''
             }
        )

        self.assertEqual(registration_response.status_code, 400)

    def test_ar_to_waiting_list(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.request_user)
        self.client.force_authenticate(self.request_user)
        self.assertEqual(self.event.waiting_registrations.count(), 0)

        registration_response = self.client.post(
            f'{_get_registrations_list_url(self.event.id)}admin_register/',
            {'user': self.user.id, 'admin_reason': 'test'}
        )

        self.assertEqual(registration_response.status_code, 201)
        self.assertEqual(self.event.waiting_registrations.count(), 1)


@skipIf(not stripe.api_key, 'No API Key set. Set STRIPE_TEST_KEY in ENV to run test.')
class StripePaymentTestCase(APITestCase):
    """
    Testing cards used:
    https://stripe.com/docs/testing#cards
    """
    fixtures = ['test_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.event = Event.objects.get(title='POOLS_AND_PRICED')

    def issue_payment(self, token):
        return self.client.post(_get_detail_url(self.event.id) + 'payment/', {'token': token.id})

    def test_payment(self):
        token = create_token('4242424242424242', '123')
        res = self.issue_payment(token)
        self.assertEqual(res.status_code, 202)
        self.assertEqual(res.data.get('charge_status'), constants.PAYMENT_PENDING)
        registration_id = res.data.get('id')
        get_object = self.client.get(_get_registrations_detail_url(self.event.id, registration_id))
        self.assertEqual(get_object.data.get('charge_status'), 'succeeded')

    def test_refund_task(self):
        token = create_token('4242424242424242', '123')
        self.issue_payment(token)
        registration = Registration.objects.get(event=self.event, user=self.abakus_user)

        stripe.Refund.create(charge=registration.charge_id)

        stripe_events_all = stripe.Event.all(limit=3)
        stripe_event = None
        for obj in stripe_events_all.data:
            if obj.data.object.id == registration.charge_id:
                stripe_event = obj
                break
        self.assertIsNotNone(stripe_event)

        stripe_webhook_event.delay(event_id=stripe_event.id, event_type='charge.refunded')

        registration.refresh_from_db()

        self.assertEqual(registration.charge_status, 'succeeded')
        self.assertEqual(registration.charge_amount, 10000)
        self.assertEqual(registration.charge_amount_refunded, 10000)


class CapacityExpansionTestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_events.yaml',
                'test_users.yaml', 'test_companies.yaml']

    def setUp(self):
        self.webkom_user = User.objects.get(pk=1)

        abakus_group = AbakusGroup.objects.get(name='Abakus')
        webkom_group = AbakusGroup.objects.get(name='Webkom')
        webkom_group.add_user(self.webkom_user)
        self.client.force_authenticate(self.webkom_user)
        event_data = _test_event_data[0]
        event_data['pools'][0]['permission_groups'] = [abakus_group.id]

        self.event_response = self.client.post(_get_list_url(), event_data)
        self.event = Event.objects.get(id=self.event_response.data.pop('id', None))
        self.event.start_time = timezone.now() + timedelta(hours=3)
        users = get_dummy_users(11)
        for user in users:
            abakus_group.add_user(user)
            registration = Registration.objects.get_or_create(event=self.event, user=user)[0]
            self.event.register(registration)
        self.assertEquals(self.event.waiting_registrations.count(), 1)
        self.updated_event = deepcopy(event_data)
        self.updated_event['pools'][0]['id'] = self.event_response.data['pools'][0]['id']

    def test_bump_on_pool_expansion(self):
        self.updated_event['pools'][0]['capacity'] = 11
        response = self.client.put(_get_detail_url(self.event.id), self.updated_event)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.event.waiting_registrations.count(), 0)

    def test_bump_on_pool_creation(self):
        self.updated_event['pools'].append(_test_pools_data[0])
        response = self.client.put(_get_detail_url(self.event.id), self.updated_event)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.event.waiting_registrations.count(), 0)

    def test_no_bump_on_reduced_pool_size(self):
        self.updated_event['pools'][0]['capacity'] = 9
        response = self.client.put(_get_detail_url(self.event.id), self.updated_event)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.event.waiting_registrations.count(), 1)
