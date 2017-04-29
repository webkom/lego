import asyncore
import smtpd

from django.conf import settings
from django.utils import timezone
from structlog import get_logger

from lego.apps.restricted.exceptions import (DefectMessageException, MessageIDNotExistException,
                                             ParseEmailException)
from lego.apps.restricted.parser import ParserMessageType
from lego.apps.restricted.utils import split_address
from lego.utils.management_command import BaseCommand

from . import channel
from .parser import LMTPEmailParser

smtpd.__version__ = 'Lego LMTP'
log = get_logger()


class LMTPService(BaseCommand, smtpd.SMTPServer):
    """
    This class provides a interface for transporting mail into LEGO using LMTP.
    Command: manage.py restricted_email
    Settings:
        LMTP_HOST = 'localhost'
        LMTP_PORT = 8024
    """

    help = 'Start a lmtp server for incoming restricted messages'
    channel_class = channel.Channel

    def run(self, *args, **kwargs):
        asyncore.loop(use_poll=True)

    def close(self):
        asyncore.socket_map.clear()
        asyncore.close_all()

    def __init__(self):
        localaddr = settings.LMTP_HOST, int(settings.LMTP_PORT)
        log.info('lmtp_server_start', address=localaddr)
        smtpd.SMTPServer.__init__(self, localaddr, remoteaddr=None)
        super().__init__()

    def handle_accept(self):
        conn, addr = self.accept()
        channel.Channel(self, conn, addr)
        log.debug('lmtp_message_accept', address=addr)

    def process_message(self, peer, mailfrom, recipients, data):
        parser = LMTPEmailParser(data, mailfrom, ParserMessageType.STRING)

        try:
            message = parser.parse()
        except ParseEmailException:
            log.exception('lmtp_email_parse_error')
            return channel.CRLF.join(channel.ERR_451 for _ in recipients)
        except MessageIDNotExistException:
            log.exception('lmtp_message_no_message_id')
            return channel.CRLF.join(channel.ERR_550_MID for _ in recipients)
        except DefectMessageException:
            log.exception('lmtp_message_defect')
            return channel.CRLF.join(channel.ERR_501 for _ in recipients)

        status = []
        for recipient in recipients:
            try:
                local, domain = split_address(recipient)
                message_data = {
                    'original_size': message.original_size,
                    'received_time': timezone.now()
                }

                print(local, domain, message_data)

                status.append(channel.OK_250)

            except Exception:
                from raven.contrib.django.raven_compat.models import client
                client.captureException()
                log.error('lmtp_lookup_failure')
                status.append(channel.ERR_550)

        return channel.CRLF.join(status)
