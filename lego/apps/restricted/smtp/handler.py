from django.conf import settings
from django.utils import timezone

from structlog import get_logger

from lego.apps.restricted.exceptions import (
    DefectMessageException,
    MessageIDNotExistException,
    ParseEmailException,
)
from lego.apps.restricted.message_processor import MessageProcessor
from lego.apps.restricted.parser import ParserMessageType

from .parser import SMTPEmailParser

log = get_logger()

CRLF = "\r\n"
ERR_451 = "451 Requested action aborted: error in processing"
ERR_501 = "501 Message has defects"
ERR_502 = "502 Error: command HELO not implemented"
ERR_511 = "511 Mailbox nonexistent"
ERR_550 = "550 Requested action not taken: mailbox unavailable"
ERR_550_MID = "550 No Message-ID header provided"
OK_250 = "250 Ok"


class RestrictedHandler:
    async def handle_DATA(self, server, session, envelope):
        data = envelope.content
        mailfrom = envelope.mail_from
        recipients = envelope.rcpt_tos

        parser = SMTPEmailParser(data, mailfrom, ParserMessageType.BYTES)

        try:
            message = parser.parse()
        except ParseEmailException:
            log.exception("smtp_email_parse_error")
            return CRLF.join(ERR_451 for _ in recipients)
        except MessageIDNotExistException:
            log.exception("smtp_message_no_message_id")
            return CRLF.join(ERR_550_MID for _ in recipients)
        except DefectMessageException:
            log.exception("smtp_message_defect")
            return CRLF.join(ERR_501 for _ in recipients)

        status = []
        for recipient in recipients:

            if recipient not in [
                settings.RESTRICTED_ADDRESS,
                f"{settings.RESTRICTED_ADDRESS}@{settings.RESTRICTED_DOMAIN}",
            ]:
                log.warn("restricted_incorrect_destination_address", address=recipient)
                return ERR_511

            try:
                message_data = {
                    "original_size": message.original_size,
                    "received_time": timezone.now(),
                }

                message_processor = MessageProcessor(mailfrom, message, message_data)
                await message_processor.process_message()

                return OK_250

            except Exception:

                log.exception("smtp_lookup_failure")
                status.append(ERR_550)

        return CRLF.join(status)
