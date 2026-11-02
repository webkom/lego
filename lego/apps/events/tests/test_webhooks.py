from unittest import mock

from django.test import override_settings
from rest_framework import status
from rest_framework.exceptions import ValidationError

import stripe
from stripe.error import SignatureVerificationError

from lego.apps.events.exceptions import WebhookDidNotFindRegistration
from lego.apps.events.models import Event, Registration
from lego.apps.events.tasks import stripe_webhook_event
from lego.apps.events.tests.utils import get_dummy_users
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
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_events.yaml",
        "test_companies.yaml",
    ]

    def stripe_event(self, stripe_object: dict) -> stripe.Event:
        return stripe.Event.construct_from(
            {"id": "evt_1", "data": {"object": stripe_object}}, "api_key"
        )

    def assert_ignored_as_external(self, mock_log, event_type: str) -> None:
        mock_log.info.assert_called_once_with(
            "stripe_webhook_ignored_external_payment",
            event_id="evt_1",
            event_type=event_type,
        )

    @mock.patch("lego.apps.events.tasks.log")
    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_ignores_external_payment_without_metadata(self, mock_retrieve, mock_log):
        """Payments created outside LEGO on the shared Stripe account are ignored"""
        mock_retrieve.return_value = self.stripe_event(
            {"id": "pi_1", "amount": 84500, "status": "succeeded", "metadata": {}}
        )

        stripe_webhook_event(event_id="evt_1", event_type="payment_intent.succeeded")

        self.assert_ignored_as_external(mock_log, "payment_intent.succeeded")

    @mock.patch("lego.apps.events.tasks.log")
    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_ignores_external_payment_with_foreign_metadata(
        self, mock_retrieve, mock_log
    ):
        """External payments are ignored even when they carry their own metadata"""
        mock_retrieve.return_value = self.stripe_event(
            {
                "id": "pi_1",
                "amount": 84500,
                "status": "succeeded",
                "metadata": {"order_id": "42"},
            }
        )

        stripe_webhook_event(event_id="evt_1", event_type="payment_intent.succeeded")

        self.assert_ignored_as_external(mock_log, "payment_intent.succeeded")

    @mock.patch("lego.apps.events.tasks.log")
    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_ignores_external_refund(self, mock_retrieve, mock_log):
        """Refunds of payments created outside LEGO are ignored"""
        mock_retrieve.return_value = self.stripe_event(
            {
                "id": "ch_1",
                "amount": 84500,
                "amount_refunded": 84500,
                "status": "succeeded",
                "payment_intent": "pi_unknown",
                "metadata": {},
            }
        )

        stripe_webhook_event(event_id="evt_1", event_type="charge.refunded")

        self.assert_ignored_as_external(mock_log, "charge.refunded")

    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_raises_for_partial_lego_metadata(self, mock_retrieve):
        """A LEGO payment with incomplete metadata must fail loudly, not be ignored"""
        mock_retrieve.return_value = self.stripe_event(
            {
                "id": "pi_1",
                "amount": 84500,
                "status": "succeeded",
                "last_payment_error": None,
                "metadata": {"EVENT_ID": 1},
            }
        )

        with self.assertRaises(ValidationError):
            stripe_webhook_event(
                event_id="evt_1", event_type="payment_intent.succeeded"
            )

    @mock.patch("lego.apps.events.tasks.stripe.Event.retrieve")
    def test_raises_for_lego_payment_with_stripped_metadata(self, mock_retrieve):
        """A payment matching a registration's payment intent must fail loudly when
        its metadata is gone, not be ignored as external"""
        event = Event.objects.get(title="POOLS_AND_PRICED")
        user = get_dummy_users(1)[0]
        Registration.objects.create(event=event, user=user, payment_intent_id="pi_1")
        mock_retrieve.return_value = self.stripe_event(
            {"id": "pi_1", "amount": 84500, "status": "succeeded", "metadata": {}}
        )

        with self.assertRaises(ValidationError):
            stripe_webhook_event(
                event_id="evt_1", event_type="payment_intent.succeeded"
            )

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
                    "EVENT_ID": 999,
                    "USER_ID": 999,
                    "USER": "Test User",
                    "EMAIL": "test@abakus.no",
                },
            }
        )

        with self.assertRaises(WebhookDidNotFindRegistration):
            stripe_webhook_event(
                event_id="evt_1", event_type="payment_intent.succeeded"
            )
