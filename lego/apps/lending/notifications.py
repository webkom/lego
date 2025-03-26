from lego.apps.notifications.constants import LENDING_REQUEST
from lego.apps.notifications.notification import Notification


class LendingRequestNotification(Notification):
    name = LENDING_REQUEST

    def generate_mail(self):
        lending_requst = self.kwargs["lending_requst"]
        lender = self.kwargs["lender"]
        return self._delay_mail(
            to_email=lender.email,
            context={
                "object_name": lending_requst.lendable_object.title,
                "object_id": lending_requst.lendable_object.id,
                "request_id": lending_requst.id,
                "lender": lender.first_name,
                "lendee": self.user.first_name,
                "start_date": lending_requst.start_date,
                "end_date": lending_requst.end_date,
                "text": lending_requst.text,
            },
            subject=f"Ny forespørsel om utlån av {lending_requst.lendable_object.title}",
            plain_template="lendingRequests/email/lending_request.txt",
            html_template="lendingRequests/email/lending_request.html",
        )
