from zoneinfo import ZoneInfo

from lego.apps.lending.constants import LENDING_REQUEST_TRANSLATION_MAP
from lego.apps.lending.models import LendingRequest, TimelineEntry
from lego.apps.notifications.constants import (
    LENDING_REQUEST,
    LENDING_REQUEST_STATUS_UPDATE,
)
from lego.apps.notifications.notification import Notification
from lego.apps.users.models import User

# Lender = person responsible for the object
# Lendee = person who wants to borrow the object


class LendingRequestNotification(Notification):
    name = LENDING_REQUEST

    def generate_mail(self):
        lending_request = self.kwargs["lending_request"]
        lender = self.kwargs["lender"]
        return self._delay_mail(
            to_email=(
                lender.internal_email_address if lender.internal_email else lender.email
            ),
            context={
                "object_name": lending_request.lendable_object.title,
                "object_id": lending_request.lendable_object.id,
                "request_id": lending_request.id,
                "lender": lender.first_name,
                "lendee": self.user.first_name,
                "start_date": lending_request.start_date.astimezone(
                    ZoneInfo("Europe/Oslo")
                ).strftime("%d.%m kl. %H:%M"),
                "end_date": lending_request.end_date.astimezone(
                    ZoneInfo("Europe/Oslo")
                ).strftime("%d.%m kl. %H:%M"),
                "text": lending_request.text,
            },
            subject=f"Ny forespørsel om utlån av {lending_request.lendable_object.title}",
            plain_template="lendingRequests/email/lending_request.txt",
            html_template="lendingRequests/email/lending_request.html",
        )


class LendingRequestStatusUpdateNotification(Notification):
    name = LENDING_REQUEST_STATUS_UPDATE

    def generate_mail(self):
        lending_request: LendingRequest = self.kwargs["lending_request"]
        timelineentry: TimelineEntry = self.kwargs["timelineentry"]
        recipient: User = self.kwargs["recipient"]
        return self._delay_mail(
            to_email=(
                recipient.internal_email_address
                if recipient.internal_email
                else recipient.email
            ),
            context={
                "object_name": lending_request.lendable_object.title,
                "object_id": lending_request.lendable_object.id,
                "request_id": lending_request.id,
                "new_status": LENDING_REQUEST_TRANSLATION_MAP[timelineentry.status],
                "recipient": recipient.full_name,
            },
            subject="Status endret på utlånsforespørsel",
            plain_template="lendingRequests/email/lending_request.txt",
            html_template="lendingRequests/email/lending_request_status_update.html",
        )
