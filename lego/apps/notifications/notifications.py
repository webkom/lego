from lego.apps.notifications.constants import ANNOUNCEMENT
from lego.apps.notifications.notification import Notification


class AnnouncementNotification(Notification):
    """
    Sent a notification to one recipient of an Announcement.
    The base class verifies the user settings.
    """

    name = ANNOUNCEMENT

    def generate_mail(self):
        """
        Generate the email message the user should receive.
        """
        announcement = self.kwargs["announcement"]

        sender = announcement.created_by.full_name
        if announcement.from_group:
            sender = announcement.from_group.name

        return self._delay_mail(
            to_email=self.user.email_address,
            context={
                "first_name": self.user.first_name,
                "sender": sender,
                "message": announcement.message,
            },
            subject=f"Kunngjøring fra {sender}",
            plain_template="notifications/email/announcement.txt",
            html_template="notifications/email/announcement.html",
        )

    def generate_push(self):
        """
        Generate the push message the user should receive on his/her phone.
        """
        announcement = self.kwargs["announcement"]

        sender = announcement.created_by.full_name
        if announcement.from_group:
            sender = announcement.from_group.name

        return self._delay_push(
            template="notifications/push/announcement.txt",
            context={"sender": sender},
            title=f"Kunngjøring fra {sender}",
            instance=announcement,
        )
