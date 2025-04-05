from lego.apps.notifications.constants import LENDING_REQUEST, LENDING_REQUEST_STATUS_UPDATE
from lego.apps.notifications.notification import Notification


# Lender = person responsible for the object
# Lendee = person who wants to borrow the object

class LendingRequestNotification(Notification):
    name = LENDING_REQUEST

    def generate_mail(self):
        lending_request = self.kwargs["lending_request"]
        lender = self.kwargs["lender"]
        return self._delay_mail(
            to_email=lender.email,
            context={
                "object_name": lending_request.lendable_object.title,
                "object_id": lending_request.lendable_object.id,
                "request_id": lending_request.id,
                "lender": lender.first_name,
                "lendee": self.user.first_name,
                "start_date": lending_request.start_date,
                "end_date": lending_request.end_date,
                "text": lending_request.text,
            },
            subject=f"Ny forespørsel om utlån av {lending_request.lendable_object.title}",
            plain_template="lendingRequests/email/lending_request.txt",
            html_template="lendingRequests/email/lending_request.html",
        )

class LendingRequestStatusUpdateNotification(Notification):
    name = LENDING_REQUEST_STATUS_UPDATE

    def generate_mail(self):
        lending_request = self.kwargs["lending_request"]
        timelineentry = self.kwargs["timelineentry"]
        recipient = self.kwargs["recipient"]
        return self._delay_mail(
            to_email=recipient.email,
            context={
                "object_name": lending_request.lendable_object.title,
                "object_id": lending_request.lendable_object.id,
                "request_id": lending_request.id,
                "new_status": timelineentry.status,
            },
            subject=f"Status endret på utlånsforespørsel om {lending_request.lendable_object.title}",
            plain_template="lendingRequests/email/lending_request.txt",
            html_template="lendingRequests/email/lending_request_status_update.html",
        )
