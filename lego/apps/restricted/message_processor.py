from django.conf import settings
from structlog import get_logger

log = get_logger()


class MessageProcessor:

    def __init__(self, local_part, domain, message, message_data):
        self.local_part = local_part
        self.domain = domain
        self.message = message
        self.message_data = message_data

    def process_message(self):
        if not self.validate_to_address():
            log.critical(
                'restricted_mail_drop', reason='invalid_destination_address',
                local_part=self.local_part, domain=self.domain
            )
            return None

        token = self.get_token()
        if not token:
            log.critical('restricted_mail_no_token_found')
            return None

    def validate_to_address(self):
        """
        Make sure the message has the correct destination address.
        """
        if self.local_part is None or self.domain is None:
            return False

        return self.local_part.lower() == settings.RESTRICTED_ADDRESS \
            and self.domain.lower() == settings.RESTRICTED_DOMAIN

    def get_token(self):
        """
        Lookup the attached token, this is used to lookup the existing restricted mail in out
        database
        """
        pass
