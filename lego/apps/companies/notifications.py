from lego.apps.notifications.constants import COMPANY_INTEREST_CREATED
from lego.apps.notifications.notification import Notification


class CompanyInterestNotification(Notification):

    name = COMPANY_INTEREST_CREATED

    def generate_mail(self):
        """
        The email for this notication is sent in the handler.
        This allows us to send it to a mailing list, instead of specific users.
        """
        pass
