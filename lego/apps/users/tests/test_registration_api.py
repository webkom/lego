from unittest import mock

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.users.registrations import Registrations


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
                Registrations.generate_registration_token('test1@user.com')
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('email'), 'test1@user.com')


class CreateRegistrationAPITestCase(APITestCase):

    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    _test_registration_data = {
        'email': 'new_test1@user.com',
        'captcha_response': 'testCaptcha'
    }

    def test_without_email(self, *args):
        response = self.client.post(_get_list_url())
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.serializers.registration.verify_captcha', return_value=True)
    def test_with_invalid_email(self, *args):
        response = self.client.post(_get_list_url(), {
            'email': 'test1@@user.com',
            'captcha_response': 'testCaptcha'
        })
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.serializers.registration.verify_captcha', return_value=False)
    def test_with_invalid_captcha(self, *args):
        response = self.client.post(_get_list_url(), self._test_registration_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.serializers.registration.verify_captcha', return_value=True)
    def test_with_valid_captcha(self, mock_verify_captcha):
        response = self.client.post(_get_list_url(), self._test_registration_data)
        self.assertEqual(response.status_code, 202)
