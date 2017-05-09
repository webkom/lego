from lego.apps.notifications.constants import RESTRICTED_MAIL_SENT
from lego.apps.notifications.notification import Notification


class RestrictedMailSentNotification(Notification):

    name = RESTRICTED_MAIL_SENT

    def generate_mail(self):
        return self._delay_mail(
            to_email=self.user.email,
            context={
                'name': self.user.full_name,
            },
            subject=f'Begrenset epost sendt ut',
            plain_template='restricted/email/process_success.txt',
            html_template='restricted/email/process_success.html',
        )
