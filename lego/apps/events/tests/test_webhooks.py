from unittest import mock

from django.test import override_settings
from rest_framework import status

import stripe
from stripe.error import SignatureVerificationError

from lego.apps.events.exceptions import WebhookDidNotFindRegistration
from lego.apps.events.tasks import stripe_webhook_event
from lego.utils.test_utils import BaseAPITestCase, BaseTestCase


@override_settings(STRIPE_WEBHOOK_SECRET="test_secret")
class StripeWebhookTestCase(BaseAPITestCase):
    def setUp(self):
        self.url = "/api/v1/webhooks-stripe/"

    def test_post_no_signature_header(self):
        """The api returns 403 when no header is provided"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch(
        "lego.apps.events.webhooks.WebhookSignature.verify_header",
        side_effect=SignatureVerificationError("error", None, None),
    )
    def test_signature_verification_fails(self, mock_verify_header):
        """The api returns 403 when an invalid header is provided"""
        response = self.client.post(self.url, {}, HTTP_STRIPE_SIGNATURE="invalid")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        mock_verify_header.assert_called_once_with("{}", "invalid", "test_secret", 300)

    @mock.patch(
        "lego.apps.events.webhooks.WebhookSignature.verify_header", return_value=None
    )
    @mock.patch(
        "lego.apps.events.webhooks.stripe_webhook_event.delay", return_value=None
    )
    def test_valid_signature(self, mock_task, mock_verify_header):
        """Make sure the task is called when a valid signature is received"""
        payload = {"id": "id", "type": "charge.refunded"}

        response = self.client.post(self.url, payload, HTTP_STRIPE_SIGNATURE="valid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_task.assert_called_once_with(event_id="id", event_type="charge.refunded")
        mock_verify_header.assert_called_once_with(
            '{"id":"id","type":"charge.refunded"}', "valid", "test_secret", 300
        )

    @mock.patch(
        "lego.apps.events.webhooks.stripe_webhook_event.delay", return_value=None
    )
    def test_deny_by_stripe_library(self, mock_webhook_event):
        payload = {"id": "id", "type": "charge.refunded"}

        response = self.client.post(self.url, payload, HTTP_STRIPE_SIGNATURE="valid")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StripeWebhookEventTaskTestCase(BaseTestCase):
    def stripe_event(self, payment_intent: dict) -> stripe.Event:
        return stripe.Event.construct_from(
            {"id": "evt_1", "data": {"object": payment_intent}}, "api_key"
        )

    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_ignores_payment_without_metadata(self, mock_retrieve):
        """Payments created outside LEGO on the shared Stripe account are ignored"""
        mock_retrieve.return_value = self.stripe_event(
            {"id": "pi_1", "amount": 84500, "status": "succeeded", "metadata": {}}
        )

        stripe_webhook_event(event_id="evt_1", event_type="payment_intent.succeeded")

    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_raises_when_lego_payment_has_no_registration(self, mock_retrieve):
        """Payments with LEGO metadata must match a registration"""
        mock_retrieve.return_value = self.stripe_event(
            {
                "id": "pi_1",
                "amount": 84500,
                "status": "succeeded",
                "last_payment_error": None,
                "metadata": {
                    "EVENT_ID": 1,
                    "USER_ID": 1,
                    "USER": "Test User",
                    "EMAIL": "test@abakus.no",
                },
            }
        )

        with self.assertRaises(WebhookDidNotFindRegistration):
            stripe_webhook_event(
                event_id="evt_1", event_type="payment_intent.succeeded"
            )
