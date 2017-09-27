from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from lego.apps.contact.send import send_message
from lego.apps.users.models import User


class SendTestCase(TestCase):

    fixtures = [
        'initial_files.yaml',
        'initial_group_texts.yaml',
        'initial_abakus_groups.yaml',
        'development_users.yaml',
        'development_memberships.yaml'
    ]

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_anonymous(self, mock_send_email):
        send_message('title', 'message', AnonymousUser(), True)
        mock_send_email.assert_called_once()

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_anonymous_user(self, mock_send_email):
        send_message('title', 'message', AnonymousUser(), False)
        mock_send_email.assert_called_once()

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_user(self, mock_send_email):
        send_message('title', 'message', User.objects.first(), False)
        mock_send_email.assert_called_once()
