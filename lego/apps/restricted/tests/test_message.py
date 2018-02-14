from email.message import Message

from lego.apps.restricted.message import EmailMessage
from lego.utils.test_utils import BaseTestCase


class MessageTestCase(BaseTestCase):
    def setUp(self):
        self.message = EmailMessage(recipient='recipient', sender='sender', message=Message())

    def test_create_message(self):
        """Test message properties"""
        self.assertEquals(self.message.recipient, 'recipient')
        self.assertEquals(self.message.from_email, 'sender')
        self.assertIsInstance(self.message.msg, Message)
        self.assertEquals(self.message.msg['To'], 'recipient')

    def test_recipients(self):
        """The recipient function returns a list with all recipients"""
        self.assertEquals(self.message.recipients(), ['recipient'])

    def test_message(self):
        """
        The message function returns the email message. This has to be an instance if MIMEMixin.
        The django email library requires this to be able to send the message.
        """
        raw_message = self.message.message()
        self.assertIsInstance(raw_message, Message)
        self.assertIsInstance(raw_message.as_string(), str)
        self.assertIsInstance(raw_message.as_bytes(), bytes)
