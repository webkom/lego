import asyncio
import smtpd
import ssl

from django.conf import settings

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP
from structlog import get_logger

from lego.utils.management_command import BaseCommand

from .handler import RestrictedHandler

smtpd.__version__ = "Lego SMTP"  # type: ignore
log = get_logger()


class SMTPService(BaseCommand, Controller):
    """
    This class provides a interface for transporting mail into LEGO using SMTP.
    Command: manage.py restricted_email
    Settings:
        SMTP_HOST = 'localhost'
        SMTP_PORT = 8024
    """

    help = "Start a smtp server for incoming restricted messages"

    def run(self, *args, **kwargs):
        self.start()
        asyncio.get_event_loop().run_forever()

    def factory(self):
        context = None
        if settings.SMTP_SSL_ENABLE:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(
                settings.SMTP_SSL_CERTIFICATE, settings.SMTP_SSL_KEY
            )
        return SMTP(
            self.handler,
            require_starttls=False,
            tls_context=context,
        )

    def __init__(self):
        hostname = settings.SMTP_HOST
        port = int(settings.SMTP_PORT)
        log.info("smtp_server_start", address=hostname, port=port)

        handler = RestrictedHandler()
        Controller.__init__(self, handler, hostname=hostname, port=port)
        super().__init__()
