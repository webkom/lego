from structlog import get_logger

from lego.apps.restricted.exceptions import MessageIDNotExistException
from lego.apps.restricted.parser import EmailParser

log = get_logger()


class LMTPEmailParser(EmailParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = log

    def parse(self):
        msg = super().parse()

        message_id = msg.get('message-id')
        if message_id is None:
            # Messages received with LMTP should contain a MESSAGE-ID header.
            raise MessageIDNotExistException

        return msg
