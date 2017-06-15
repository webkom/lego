from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings

from lego.apps.restricted.message_processor import MessageProcessor
from lego.apps.restricted.models import RestrictedMail
from lego.apps.restricted.parser import EmailParser, ParserMessageType
from lego.apps.restricted.tests.utils import read_file


class MessageProcessorTestCase(TestCase):

    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml', 'test_companies.yaml',
                'test_events.yaml', 'test_restricted_mails.yaml']

    def setUp(self):
        raw_message = read_file(f'{settings.BASE_DIR}/apps/restricted/fixtures/emails/valid.txt')
        parser = EmailParser(raw_message, 'test@test.com', ParserMessageType.STRING)
        self.message = parser.parse()
        self.processor = MessageProcessor('test@test.com', self.message, {})

    @override_settings(
        RESTRICTED_ALLOW_ORIGINAL_SENDER=False, RESTRICTED_FROM='restricted@test.com'
    )
    def test_get_sender_settings_override(self):
        """
        Return sender configured in the settings when RESTRICTED_ALLOW_ORIGINAL_SENDER is False
        """
        restricted_mail = RestrictedMail.objects.get(id=1)
        self.assertEquals('restricted@test.com', self.processor.get_sender(restricted_mail))

    @override_settings(
        RESTRICTED_ALLOW_ORIGINAL_SENDER=True, RESTRICTED_FROM='restricted@test.com'
    )
    def test_get_sender(self):
        """Return the original sender when the settings allow it"""
        restricted_mail = RestrictedMail.objects.get(id=1)
        self.assertEquals('test@test.com', self.processor.get_sender(restricted_mail))

    @override_settings(
        RESTRICTED_ALLOW_ORIGINAL_SENDER=True, RESTRICTED_FROM='restricted@test.com'
    )
    def test_get_sender_hidden(self):
        """Return the sender form the settings when the original sender hides the address"""
        restricted_mail = RestrictedMail.objects.get(id=1)
        restricted_mail.hide_sender = True
        restricted_mail.save()

        self.assertEquals('restricted@test.com', self.processor.get_sender(restricted_mail))

    @mock.patch(
        'lego.apps.restricted.message_processor.RestrictedMail.get_restricted_mail',
        return_value=None
    )
    def test_lookup_instance(self, mock_instance_lookup):
        """Call the RestrictedMail.get_restricted_mail for instance lookup"""
        self.processor.lookup_instance('sender', 'token')
        mock_instance_lookup.assert_called_once_with('sender', 'token')

    def test_rewrite_message(self):
        """Remove headers that may cause problems. Only keep a few required headers."""
        raw_message = read_file(
            f'{settings.BASE_DIR}/apps/restricted/fixtures/emails/clean_headers.txt'
        )
        parser = EmailParser(raw_message, 'test@test.com', ParserMessageType.STRING)
        message = parser.parse()
        new_message = self.processor.rewrite_message(message, 'test@test.com')

        self.assertCountEqual([
            'From', 'Subject', 'Content-Type', 'MIME-Version', 'Sender'
        ], new_message.keys())

    def test_decorate(self):
        """Simple smoke-test, just make sure the function not raises an error"""
        payloads = len(self.message.get_payload())

        self.processor.decorate(self.message, False, 'test@test.com')
        self.assertTrue(len(self.message.get_payload()) > payloads)

    def test_send(self):
        """Test the outbox and make sure we have correct headers in the messages."""
        raw_message = read_file(
            f'{settings.BASE_DIR}/apps/restricted/fixtures/emails/clean_headers.txt'
        )
        parser = EmailParser(raw_message, 'test@test.com', ParserMessageType.STRING)
        message = parser.parse()
        new_message = self.processor.rewrite_message(message, 'test@test.com')

        messages = self.processor.send(
            ['test1@test.com', 'test2@test.com'], 'test@test.com', new_message
        )
        self.assertEquals(2, messages)

        outbox = mail.outbox
        first_message = outbox[0].message()
        self.assertSequenceEqual(
            ['Subject', 'Content-Type', 'MIME-Version', 'Sender', 'From', 'To'],
            first_message.keys()
        )
