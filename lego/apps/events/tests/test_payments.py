from unittest import skipIf

import stripe
from celery import chain
from django.utils import timezone
from rest_framework.test import APITestCase

from lego.apps.events.models import Event
from lego.apps.events.tasks import async_payment, registration_save
from lego.apps.users.models import AbakusGroup, User


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

    @staticmethod
    def create_token(number, cvc):
        return stripe.Token.create(
            card={
                'number': number,
                'exp_month': 12,
                'exp_year': timezone.now().year + 1,
                'cvc': cvc
            },
        )

    def test_card_declined(self):
        token = self.create_token('4000000000000002', '123')
        registration = self.event.get_registration(self.abakus_user)
        with self.assertRaises(stripe.error.StripeError):
            chain(
                async_payment.s(registration.id, token),
                registration_save.s(registration.id)
            ).delay()

        registration.refresh_from_db()
        self.assertEqual(registration.charge_status, 'card_declined')

    def test_card_incorrect_cvc(self):
        token = self.create_token('4000000000000127', '123')
        registration = self.event.get_registration(self.abakus_user)
        with self.assertRaises(stripe.error.StripeError):
            chain(
                async_payment.s(registration.id, token),
                registration_save.s(registration.id)
            ).delay()

        registration.refresh_from_db()
        self.assertEqual(registration.charge_status, 'incorrect_cvc')

    def test_card_invalid_request(self):
        token = {'token': 'invalid'}
        registration = self.event.get_registration(self.abakus_user)
        chain(
            async_payment.s(registration.id, token),
            registration_save.s(registration.id)
        ).delay()

        registration.refresh_from_db()
        self.assertEqual(registration.charge_status, 'invalid_request_error')
