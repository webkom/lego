from lego.apps.notifications.constants import COMPANY_INTEREST_CREATED
from lego.apps.notifications.notification import Notification


class CompanyInterestNotification(Notification):

    name = COMPANY_INTEREST_CREATED

    def generate_mail(self):

        company_interest = self.kwargs['company_interest']

        return self._delay_mail(
            to_email=self.user.email,
            context=company_interest.generate_mail_context(),
            subject='En ny bedrift har meldt sin interesse',
            plain_template='companies/email/company_interest.txt',
            html_template='companies/email/company_interest.html',
        )
