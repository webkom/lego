import asyncore
import smtpd

from django.conf import settings
from django.utils import timezone
from structlog import get_logger

from lego.apps.restricted.exceptions import (DefectMessageException, MessageIDNotExistException,
                                             ParseEmailException)
from lego.apps.restricted.message_processor import MessageProcessor
from lego.apps.restricted.parser import ParserMessageType
from lego.apps.stats.statsd_client import statsd
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

    @statsd.timer('restricted_mail.process_message')
    def process_message(self, peer, mailfrom, recipients, data, **kwargs):
        parser = LMTPEmailParser(data, mailfrom, ParserMessageType.BYTES)

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

            if recipient not in [
                settings.RESTRICTED_ADDRESS,
                f'{settings.RESTRICTED_ADDRESS}@{settings.RESTRICTED_DOMAIN}'
            ]:
                log.warn('restricted_incorrect_destination_address', address=recipient)
                return status.append(channel.ERR_511)

            try:
                message_data = {
                    'original_size': message.original_size,
                    'received_time': timezone.now()
                }

                message_processor = MessageProcessor(mailfrom, message, message_data)
                message_processor.process_message()

                return status.append(channel.OK_250)

            except Exception:
                from raven.contrib.django.raven_compat.models import client
                client.captureException()
                log.exception('lmtp_lookup_failure')
                status.append(channel.ERR_550)

        return channel.CRLF.join(status)
