import email
from email.message import Message

from structlog import get_logger

from .exceptions import DefectMessageException, ParseEmailException

log = get_logger()


class ParserMessageType:
    """
    Different types of message formats to parse.
    """
    STRING = 'string'
    BYTES = 'bytes'
    BINARY_FILE = 'binary_file'


class EmailParser:

    def __init__(self, raw_message, mail_from, message_type):
        self.raw_message = raw_message
        self.mail_from = mail_from
        self.message_type = message_type
        self.log = log

    def parse(self):
        try:
            if self.message_type == ParserMessageType.STRING:
                msg = email.message_from_string(self.raw_message, Message)
            elif self.message_type == ParserMessageType.BYTES:
                msg = email.message_from_bytes(self.raw_message, Message)
            elif self.message_type == ParserMessageType.BINARY_FILE:
                msg = email.message_from_binary_file(self.raw_message, Message)
            else:
                raise ValueError('Invalid message_type, could not parse message.')
        except Exception:
            raise ParseEmailException

        # Do basic post-processing of the message, checking it for defects or
        # other missing information.
        if msg.defects:
            raise DefectMessageException

        # Add headers used in by LEGO
        msg.original_size = len(self.raw_message)
        msg['X-MailFrom'] = self.mail_from

        return msg
