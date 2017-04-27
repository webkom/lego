from unittest import mock

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APITransactionTestCase

from lego.apps.users.models import User


def _get_list_url():
    return reverse('api:v1:user-registration-list')


def _get_registration_token_url(token):
    return f'{_get_list_url()}?token={token}'


class RetrieveRegistrationAPITestCase(APITestCase):
    def test_without_token(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 400)

    def test_with_empty_token(self):
        response = self.client.get(_get_registration_token_url(''))
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_token(self):
        response = self.client.get(_get_registration_token_url('InvalidToken'))
        self.assertEqual(response.status_code, 400)

    def test_with_valid_token(self):
        response = self.client.get(
            _get_registration_token_url(
                User.generate_registration_token('TestUsername')
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('username'), 'TestUsername')


class CreateRegistrationAPITestCase(APITransactionTestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    _test_registration_data = {
        'username': 'new_testuser',
        'captcha_response': 'testCaptcha'
    }

    def test_without_username(self, *args):
        response = self.client.post(_get_list_url())
        self.assertEqual(response.status_code, 400)

    def test_with_existing_username(self, *args):
        response = self.client.post(_get_list_url(), {
            'username': 'test1',
            'captcha_response': 'testCaptcha'
        })
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_username(self, *args):
        response = self.client.post(_get_list_url(), {
            'username': 'test_u$er',
            'captcha_response': 'testCaptcha'
        })
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.views.registration.verify_captcha', return_value=False)
    def test_with_invalid_captcha(self, *args):
        response = self.client.post(_get_list_url(), self._test_registration_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.views.registration.verify_captcha', return_value=True)
    def test_with_valid_captcha(self, mock_verify_captcha):
        response = self.client.post(_get_list_url(), self._test_registration_data)
        self.assertEqual(response.status_code, 202)
