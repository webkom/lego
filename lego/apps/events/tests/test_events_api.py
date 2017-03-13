from datetime import timedelta
from unittest import mock, skipIf

import stripe
from django.core.urlresolvers import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APITransactionTestCase

from lego.apps.events import constants
from lego.apps.events.models import Event, Registration
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


def _get_webhook_url():
    return reverse('api:v1:webhooks-list')


class ListEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
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
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
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


class CreateEventsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        self.event_response = self.client.post(_get_list_url(), _test_event_data[0])
        self.assertEqual(self.event_response.status_code, 201)
        self.event_id = self.event_response.data.pop('id', None)
        self.pool_response = self.client.post(_get_pools_list_url(self.event_id),
                                              _test_pools_data[0])
        self.pool_id = self.pool_response.data.get('id', None)

    def test_event_creation(self):
        self.assertIsNotNone(self.event_id)
        self.assertEqual(self.event_response.status_code, 201)

    def test_event_update(self):
        event_update_response = self.client.put(_get_detail_url(self.event_id), _test_event_data[1])
        res_event = event_update_response.data
        expect_event = _test_event_data[1]
        for key in ['title', 'description', 'text', 'start_time', 'end_time', 'merge_time']:
            self.assertEqual(res_event[key], expect_event[key])

        self.assertEqual(self.event_id, event_update_response.data.pop('id'))
        self.assertEqual(event_update_response.status_code, 200)

    def test_pool_creation(self):
        self.assertIsNotNone(self.pool_response.data.pop('id'))
        self.assertEqual(self.pool_response.status_code, 201)
        self.assertEqual(_test_pools_data[0], self.pool_response.data)

    def test_pool_update(self):
        pool_update_response = self.client.put(
            _get_pools_detail_url(self.event_id, self.pool_id), _test_pools_data[1]
        )
        pool_get_response = self.client.get(_get_pools_detail_url(self.event_id, self.pool_id))
        pool_get_response.data.pop('registrations')  # The put does not return updated data
        pool_get_response.data.pop('action_grant')  # We don't care about permissions here

        self.assertEqual(pool_update_response.status_code, 200)
        self.assertIsNotNone(pool_get_response.data.pop('id'))
        self.assertEqual(pool_get_response.data['name'], _test_pools_data[1]['name'])
        self.assertEqual(pool_get_response.data['capacity'], _test_pools_data[1]['capacity'])
        self.assertEqual(
            pool_get_response.data['activation_date'], _test_pools_data[1]['activation_date']
        )
        self.assertEqual(
            pool_get_response.data['permission_groups'][0]['id'],
            _test_pools_data[1]['permission_groups'][0]
        )


class PoolsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.all().first()

    def test_with_group_permission(self):
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 200)

    def test_with_bedkom_group_permission(self):
        AbakusGroup.objects.get(name='Bedkom').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 200)

    def test_without_group_permission(self):
        self.client.force_authenticate(self.abakus_user)
        pool_response = self.client.get(_get_pools_detail_url(1, 1))
        self.assertEqual(pool_response.status_code, 403)

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


@mock.patch('lego.apps.events.views.verify_captcha', return_value=True)
class RegistrationsTestCase(APITransactionTestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        Event.objects.all().update(start_time=timezone.now() + timedelta(hours=3))
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Abakus').add_user(self.abakus_user)
        self.client.force_authenticate(self.abakus_user)

    def test_create(self, mock_verify_captcha):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(registration_response.data.get('status'), constants.PENDING_REGISTER)
        res = self.client.get(_get_registrations_detail_url(
            event.id, registration_response.data['id'])
        )
        self.assertEqual(res.data['user']['id'], 1)
        self.assertEqual(res.data['status'], constants.SUCCESS_REGISTER)

    def test_unable_to_create(self, mock_verify_captcha):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        self.non_abakus_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name='Users').add_user(self.non_abakus_user)
        self.client.force_authenticate(self.non_abakus_user)
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 403)

    def test_update(self, mock_verify_captcha):
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 202)
        res = self.client.patch(
            _get_registrations_detail_url(event.id, registration_response.data['id']),
            {'feedback': 'UPDATED'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['feedback'], 'UPDATED')

    def test_user_cannot_update_other_registration(self, mock_verify_captcha):
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

    def test_admin_update_registration(self, mock_verify_captcha):
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

    def test_register_no_pools(self, mock_verify_captcha):
        event = Event.objects.get(title='NO_POOLS_ABAKUS')
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(registration_response.data.get('status'), constants.PENDING_REGISTER)
        res = self.client.get(_get_registrations_list_url(event.id))
        for user in res.data['results']:
            self.assertEqual(user.get('status', None), constants.FAILURE_REGISTER)

    def test_unregister(self, mock_verify_captcha):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        registration = Registration.objects.get(user=self.abakus_user, event=event)
        registration_response = self.client.delete(_get_registrations_detail_url(event.id,
                                                                                 registration.id))

        get_unregistered = self.client.get(_get_registrations_detail_url(event.id, registration.id))
        self.assertEqual(registration_response.status_code, 202)
        self.assertEqual(get_unregistered.status_code, 404)

    def test_can_not_unregister_other_user(self, mock_verify_captcha):
        event = Event.objects.get(title='POOLS_WITH_REGISTRATIONS')
        registration = Registration.objects.get(user=self.abakus_user, event=event)

        self.other_user = User.objects.get(pk=2)
        AbakusGroup.objects.get(name='Abakus').add_user(self.other_user)
        self.client.force_authenticate(self.other_user)
        registration_response = self.client.delete(_get_registrations_detail_url(event.id,
                                                                                 registration.id))

        self.assertEqual(registration_response.status_code, 403)

    def test_required_feedback_failing(self, mock_verify_captcha):
        """Test that register returns 400 when not providing feedback when required"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.feedback_required = True
        event.save()
        registration_response = self.client.post(_get_registrations_list_url(event.id), {})
        self.assertEqual(registration_response.status_code, 400)

    def test_required_feedback_success(self, mock_verify_captcha):
        """Test that register returns 202 when providing feedback when required"""
        event = Event.objects.get(title='POOLS_NO_REGISTRATIONS')
        event.feedback_required = True
        event.save()
        registration_response = self.client.post(
            _get_registrations_list_url(event.id), {'feedback': 'TEST'}
        )
        self.assertEqual(registration_response.status_code, 202)


class ListRegistrationsTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
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


class CreateAdminRegistrationTestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
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

        self.assertEqual(registration_response.status_code, 403)
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


@skipIf(not stripe.api_key, 'No API Key set. Set STRIPE_TEST_KEY in ENV to run test.')
class StripePaymentTestCase(APITestCase):
    """
    Testing cards used:
    https://stripe.com/docs/testing#cards
    """
    fixtures = ['initial_abakus_groups.yaml', 'test_companies.yaml', 'test_events.yaml',
                'test_users.yaml']

    def setUp(self):
        self.abakus_user = User.objects.get(pk=1)
        AbakusGroup.objects.get(name='Webkom').add_user(self.abakus_user)
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

    def test_refund_webhook(self):
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

        webhook = self.client.post(_get_webhook_url(), {
            'id': stripe_event.id,
            'type': 'charge.refunded'
        })

        registration.refresh_from_db()

        self.assertEqual(webhook.status_code, 200)
        self.assertEqual(registration.charge_status, 'succeeded')
        self.assertEqual(registration.charge_amount, 10000)
        self.assertEqual(registration.charge_amount_refunded, 10000)
