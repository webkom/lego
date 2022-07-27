from email.message import Message

from django.conf import settings

from lego.apps.restricted.parser import EmailParser, ParserMessageType
from lego.utils.test_utils import BaseTestCase

from .utils import read_file


class EmailParserTestCase(BaseTestCase):
    def test_parse_valid_email(self):
        """Try to parse a valid message, make sure we add the correct properties to the message."""
        raw_message = read_file(
            f"{settings.BASE_DIR}/apps/restricted/fixtures/emails/valid.txt"
        )

        parser = EmailParser(raw_message, "test@test.com", ParserMessageType.STRING)
        message = parser.parse()

        self.assertIsInstance(message, Message)
        self.assertEqual(message.original_size, len(raw_message))
        self.assertEqual(message["X-MailFrom"], "test@test.com")
        self.assertEqual(message["To"], "restricted@abakus.no")
