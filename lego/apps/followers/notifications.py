from lego.apps.notifications.constants import REGISTRATION_REMINDER
from lego.apps.notifications.notification import Notification


class RegistrationReminderNotification(Notification):

    name = REGISTRATION_REMINDER

    def generate_mail(self):
        event = self.kwargs["event"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "name": self.user.full_name,
                "event": event.title,
                "event_id": event.id,
            },
            subject=f"Påminnelse",
            plain_template="followers/email/reminder.txt",
            html_template="followers/email/reminder.html",
        )

    def generate_push(self):
        event = self.kwargs["event"]

        return self._delay_push(
            template="followers/email/reminder.txt",
            context={"name": self.user.full_name,
                     "event": event.title},
            instance=event,
        )
