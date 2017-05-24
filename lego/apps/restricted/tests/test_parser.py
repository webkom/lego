from email.message import Message

from django.conf import settings
from django.test import TestCase

from lego.apps.restricted.parser import EmailParser, ParserMessageType

from .utils import read_file


class EmailParserTestCase(TestCase):

    def test_parse_valid_email(self):
        """Try to parse a valid message, make sure we add the correct properties to the message."""
        raw_message = read_file(
            f'{settings.BASE_DIR}/apps/restricted/fixtures/emails/valid.txt'
        )

        parser = EmailParser(raw_message, 'test@test.com', ParserMessageType.STRING)
        message = parser.parse()

        self.assertIsInstance(message, Message)
        self.assertEquals(message.original_size, len(raw_message))
        self.assertEquals(message['X-MailFrom'], 'test@test.com')
        self.assertEquals(message['To'], 'restricted@abakus.no')
