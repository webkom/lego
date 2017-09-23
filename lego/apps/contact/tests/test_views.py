from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from lego.apps.users.models import User


class ContactViewSetTestCase(APITestCase):

    fixtures = [
        'initial_files.yaml',
        'test_abakus_groups.yaml',
        'development_users.yaml',
        'development_memberships.yaml'
    ]

    def setUp(self):
        self.url = '/api/v1/contact-form/'
        self.user = User.objects.first()

    @mock.patch('lego.apps.contact.views.send_message')
    @mock.patch('lego.apps.contact.serializers.verify_captcha', return_value=True)
    def test_without_auth(self, mock_verify_captcha, mock_send_message):
        response = self.client.post(self.url, {
            'title': 'title',
            'message': 'message',
            'anonymous': True,
            'captcha_response': 'test'
        })
        self.assertEquals(status.HTTP_202_ACCEPTED, response.status_code)
        mock_verify_captcha.assert_called_once()

    @mock.patch('lego.apps.contact.views.send_message')
    @mock.patch('lego.apps.contact.serializers.verify_captcha', return_value=True)
    def test_without_auth_not_anonymous(self, mock_verify_captcha, mock_send_message):
        response = self.client.post(self.url, {
            'title': 'title',
            'message': 'message',
            'anonymous': False,
            'captcha_response': 'test'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch('lego.apps.contact.views.send_message')
    @mock.patch('lego.apps.contact.serializers.verify_captcha', return_value=True)
    def test_with_auth(self, mock_verify_captcha, mock_send_message):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'title': 'title',
            'message': 'message',
            'anonymous': True,
            'captcha_response': 'test'
        })
        self.assertEquals(status.HTTP_202_ACCEPTED, response.status_code)
        mock_verify_captcha.assert_called_once()
        mock_send_message.assert_called_once_with(
            'title',
            'message',
            self.user,
            True
        )

    @mock.patch('lego.apps.contact.views.send_message')
    @mock.patch('lego.apps.contact.serializers.verify_captcha', return_value=False)
    def test_with_auth_invalid_captcha(self, mock_verify_captcha, mock_send_message):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {
            'title': 'title',
            'message': 'message',
            'anonymous': True,
            'captcha_response': 'test'
        })
        self.assertEquals(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_verify_captcha.assert_called_once()
