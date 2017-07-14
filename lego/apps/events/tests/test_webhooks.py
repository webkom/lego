from unittest import mock

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from stripe import SignatureVerificationError


@override_settings(STRIPE_WEBHOOK_SECRET='test_secret')
class StripeWebhookTestCase(APITestCase):

    def setUp(self):
        self.url = '/api/v1/webhooks-stripe/'

    def test_post_no_signature_header(self):
        """The api returns 403 when no header is provided"""
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('lego.apps.events.webhooks.WebhookSignature.verify_header',
                side_effect=SignatureVerificationError('error', None, None))
    def test_signature_verification_fails(self, mock_verify_header):
        """The api returns 403 when an invalid header is provided"""
        response = self.client.post(self.url, {}, HTTP_STRIPE_SIGNATURE='invalid')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

        mock_verify_header.assert_called_once_with(
            '{}', 'invalid', 'test_secret', 300
        )

    @mock.patch('lego.apps.events.webhooks.WebhookSignature.verify_header', return_value=None)
    @mock.patch('lego.apps.events.webhooks.stripe_webhook_event.delay', return_value=None)
    def test_valid_signature(self, mock_task, mock_verify_header):
        """Make sure the task is called when a valid signature is received"""
        payload = {
            'id': 'id',
            'type': 'charge.refunded'
        }

        response = self.client.post(self.url, payload, HTTP_STRIPE_SIGNATURE='valid')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        mock_task.assert_called_once_with(event_id='id', event_type='charge.refunded')
        mock_verify_header.assert_called_once_with(
            '{"id":"id","type":"charge.refunded"}', 'valid', 'test_secret', 300
        )

    @mock.patch('lego.apps.events.webhooks.stripe_webhook_event.delay', return_value=None)
    def test_deny_by_stripe_library(self, mock_webhook_event):
        payload = {
            'id': 'id',
            'type': 'charge.refunded'
        }

        response = self.client.post(self.url, payload, HTTP_STRIPE_SIGNATURE='valid')
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
