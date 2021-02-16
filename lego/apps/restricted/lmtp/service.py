import asyncio
import smtpd
import ssl

from django.conf import settings
from django.utils import timezone

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Debugging
from aiosmtpd.lmtp import LMTP
from structlog import get_logger

from lego.apps.restricted.exceptions import (
    DefectMessageException,
    MessageIDNotExistException,
    ParseEmailException,
)
from lego.apps.restricted.message_processor import MessageProcessor
from lego.apps.restricted.parser import ParserMessageType
from lego.utils.management_command import BaseCommand

from .handler import RestrictedHandler
from .parser import LMTPEmailParser

smtpd.__version__ = "Lego LMTP"
log = get_logger()


class LMTPService(BaseCommand, Controller):
    """
    This class provides a interface for transporting mail into LEGO using LMTP.
    Command: manage.py restricted_email
    Settings:
        LMTP_HOST = 'localhost'
        LMTP_PORT = 8024
    """

    help = "Start a lmtp server for incoming restricted messages"

    def run(self, *args, **kwargs):
        self.start()
        asyncio.new_event_loop().run_forever()

    def factory(self):
        context = None
        if hasattr(settings, "LMTP_SSL_CERTIFICATE"):
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(
                settings.LMTP_SSL_CERTIFICATE, settings.LMTP_SSL_KEY
            )
        return LMTP(
            self.handler,
            require_starttls=True,
            tls_context=context if context is not None else None,
        )

    def __init__(self):
        hostname = settings.LMTP_HOST
        port = int(settings.LMTP_PORT)
        log.info("lmtp_server_start", address=hostname, port=port)

        handler = RestrictedHandler()
        Controller.__init__(self, handler, hostname="localhost", port=port)
        super().__init__()
