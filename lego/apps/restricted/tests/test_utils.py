from django.conf import settings
from django.test import TestCase

from lego.apps.restricted.parser import EmailParser, ParserMessageType
from lego.apps.restricted.utils import get_mail_token

from .utils import read_file


class EmailTokenTestCase(TestCase):

    def test_parse_valid_message(self):
        """Try to parse a valid message and make sure ve remove the token payload"""
        raw_message = read_file(f'{settings.BASE_DIR}/apps/restricted/fixtures/emails/valid.txt')
        parser = EmailParser(raw_message, 'test@test.com', ParserMessageType.STRING)
        message = parser.parse()
        payloads = len(message.get_payload())

        token = get_mail_token(message)
        self.assertEquals('test_token', token)

        self.assertEquals(len(message.get_payload()), payloads-1)

    def test_parse_message_no_token(self):
        """Parsing a message with no token has no effect, the function returns None"""
        raw_message = read_file(f'{settings.BASE_DIR}/apps/restricted/fixtures/emails/no_token.txt')
        parser = EmailParser(raw_message, 'test@test.com', ParserMessageType.STRING)
        message = parser.parse()

        token = get_mail_token(message)
        self.assertIsNone(token)
