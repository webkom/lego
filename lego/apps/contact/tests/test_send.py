from unittest import mock

from django.contrib.auth.models import AnonymousUser

from lego.apps.contact.send import send_message
from lego.apps.users.models import User
from lego.utils.test_utils import BaseTestCase

default_values = {
    'from_email': None,
    'html_template': 'contact/email/contact_form.html',
    'plain_template': 'contact/email/contact_form.txt',
    'subject': 'Ny henvendelse fra kontaktskjemaet'
}


class SendTestCase(BaseTestCase):

    fixtures = [
        'initial_files.yaml', 'initial_abakus_groups.yaml', 'development_users.yaml',
        'development_memberships.yaml'
    ]

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_anonymous(self, mock_send_email):
        """
        Send in a contact form as not logged in user, set to be anonymous
        """
        anonymus_user = AnonymousUser()

        send_message('title', 'message', anonymus_user, True)
        mock_send_email.assert_called_with(
            to_email="hs@abakus.no", context={
                'title': 'title',
                'message': 'message',
                'from_name': "Anonymous",
                'from_email': "Unknown"
            }, **default_values
        )
        mock_send_email.assert_called_once()

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_anonymous_user(self, mock_send_email):
        """
        Send in a contact form as not logged in user
        """
        anonymus_user = AnonymousUser()

        send_message('title', 'message', anonymus_user, False)
        mock_send_email.assert_called_with(
            to_email="hs@abakus.no", context={
                'title': 'title',
                'message': 'message',
                'from_name': "Anonymous",
                'from_email': "Unknown"
            }, **default_values
        )
        mock_send_email.assert_called_once()

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_user(self, mock_send_email):
        """
        Send in a contact form as logged in user, showing name
        """
        logged_in_user = User.objects.first()

        send_message('title', 'message', logged_in_user, False)
        mock_send_email.assert_called_with(
            to_email="hs@abakus.no", context={
                'title': 'title',
                'message': 'message',
                'from_name': logged_in_user.full_name,
                'from_email': logged_in_user.email_address
            }, **default_values
        )
        mock_send_email.assert_called_once()

    @mock.patch('lego.apps.contact.send.send_email.delay')
    def test_send_user_set_anonymous(self, mock_send_email):
        """
        Send in a contact form as logged in user, set to be anonymous
        """
        logged_in_user = User.objects.first()

        send_message('title', 'message', logged_in_user, True)
        mock_send_email.assert_called_with(
            to_email="hs@abakus.no", context={
                'title': 'title',
                'message': 'message',
                'from_name': "Anonymous",
                'from_email': "Unknown"
            }, **default_values
        )
        mock_send_email.assert_called_once()
