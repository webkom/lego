from copy import deepcopy
from email.message import Message
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import get_connection
from structlog import get_logger

from lego.apps.action_handlers.registry import get_handler
from lego.apps.restricted.models import RestrictedMail

from .message import EmailMessage
from .utils import get_mail_token

log = get_logger()


class MessageProcessor:
    """
    Pipeline for message processing after initial parsing is done by the LMTP server.
    """

    def __init__(self, sender, message, message_data):
        self.sender = sender
        self.message = message
        self.message_data = message_data
        self.action_handler = get_handler(RestrictedMail)

    def process_message(self):
        token = self.get_token(self.message)
        if not token:
            log.critical('restricted_mail_no_token_found', sender=self.sender)
            # Notify about failure
            self.action_handler.run(None, 'failure', sender=self.sender, reason='TOKEN_NOT_FOUND')
            return None

        restricted_message = self.lookup_instance(self.sender, token)
        if restricted_message is None:
            log.critical('restricted_mail_token_not_found')
            # Notify about failure
            self.action_handler.run(None, 'failure', sender=self.sender, reason='TOKEN_INVALID')
            return None

        recipients = restricted_message.lookup_recipients()
        sender = self.get_sender(restricted_message)

        message = self.rewrite_message(self.message, sender)

        if sender == settings.RESTRICTED_FROM:
            # Add a footer with a note about the from address rewrite.
            self.decorate(message, restricted_message.hide_sender, self.sender)

        self.send(recipients, sender, message)
        restricted_message.mark_used()

        # Send a success message to the creator
        self.action_handler.run(restricted_message, 'sent')

    def get_sender(self, restricted_mail):
        """
        Get the sender address. We use the global settings and the restricted_mail object to find
        the sender.
        """

        if settings.RESTRICTED_ALLOW_ORIGINAL_SENDER and not restricted_mail.hide_sender:
            return self.sender

        return settings.RESTRICTED_FROM

    @staticmethod
    def get_token(message):
        """
        Lookup the attached token, this is used to lookup the existing restricted mail in our
        database.
        """
        return get_mail_token(message)

    @staticmethod
    def lookup_instance(sender, token):
        """
        Get the restricted_mail instance based on a token found in the received message.
        """
        return RestrictedMail.get_restricted_mail(sender, token)

    @staticmethod
    def rewrite_message(message, sender):
        """
        This function replaces the headers in the message. We preserve the headers in the
        preserve_headers list, all other headers is removed. We do this to get a higher chance to
        pass thinks like SPF and DKIM checks. These headers is added automatically by our outgoing
        mail handler if the sender address is valid and managed by us.
        """
        preserve_headers = ['Subject', 'Content-Type', 'MIME-Version']
        headers = {}

        for header in preserve_headers:
            header_value = message.get(header)
            if header_value:
                headers[header] = header_value

        message._headers = []

        for header, value in headers.items():
            message[header] = value

        message['Sender'] = sender
        message['From'] = sender

        return message

    @staticmethod
    def send(recipients, sender, message):
        """
        Create a new connection and bulk send mails
        """
        connection = get_connection(fail_silently=False)
        messages = [EmailMessage(recipient, sender, deepcopy(message)) for recipient in recipients]
        log.info('restricted_mail_process_messages', sender=sender, recipients=len(messages))
        return connection.send_messages(messages)

    @staticmethod
    def decorate(message, hide_sender, sender):
        """
        Notify the recipient about the sender rewrite.
        """

        footer = ['------------', 'Du kan ikke svare direkte på denne eposten.']

        if not hide_sender:
            footer.append(f'Opprinnelig avsender er {sender}, send svar til denne adressen.')
            footer.append(
                'Denne eposten har uorginal avsender for å redusere risikoen for at '
                'meldingen oppfattes som spam.'
            )
        else:
            footer.append('Opprinnelig avsender har valgt å skjule sin adresse.')

        footer = '\n'.join(footer)
        charset = message.get_content_charset() or 'us-ascii'
        content_type = message.get_content_type()

        wrap = True
        if not message.is_multipart() and content_type == 'text/plain':
            format_param = message.get_param('format')
            delsp = message.get_param('delsp')
            transfer_encoding = message.get('content-transfer-encoding')

            try:
                old_payload = message.get_payload(decode=True).decode(charset)
                del message['content-transfer-encoding']

                footer_separator = '\n'
                payload = old_payload + footer_separator + footer

                for cset in (charset, 'utf-8'):
                    try:
                        message.set_payload(payload.encode(cset), cset)
                    except UnicodeError:
                        pass
                    else:
                        if format_param:
                            message.set_param('format', format_param)
                        if delsp:
                            message.set_param('delsp', delsp)
                        wrap = False
                        break
            except (LookupError, UnicodeError):
                if transfer_encoding:
                    del message['content-transfer-encoding']
                    message['Content-Transfer-Encoding'] = transfer_encoding

        elif message.get_content_type() == 'multipart/mixed':
            payload = message.get_payload()
            if not isinstance(payload, list):
                payload = [payload]

            mime_footer = MIMEText(footer.encode('utf-8'), 'plain', 'utf-8')
            mime_footer['Content-Disposition'] = 'inline'
            payload.append(mime_footer)
            message.set_payload(payload)
            wrap = False

        if not wrap:
            return

        inner = Message()
        for h, v in message.items():
            if h.lower().startswith('content-'):
                inner[h] = v
        inner.set_payload(message.get_payload())
        inner.set_unixfrom(message.get_unixfrom())
        inner.preamble = message.preamble
        inner.epilogue = message.epilogue
        inner.set_default_type(message.get_default_type())
        if hasattr(message, '__version__'):
            inner.__version__ = message.__version__
        payload = [inner]
        mime_footer = MIMEText(footer.encode('utf-8'), 'plain', 'utf-8')
        mime_footer['Content-Disposition'] = 'inline'
        payload.append(mime_footer)
        message.set_payload(payload)
        del message['content-type']
        del message['content-transfer-encoding']
        del message['content-disposition']
        message['Content-Type'] = 'multipart/mixed'
