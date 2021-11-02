from datetime import timedelta

from lego.apps.notifications.constants import (
    DELETED_WARNING,
    INACTIVE_WARNING,
    PENALTY_CREATION,
)
from lego.apps.notifications.notification import Notification


class PenaltyNotification(Notification):

    name = PENALTY_CREATION

    def generate_mail(self):
        penalty = self.kwargs["penalty"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "first_name": self.user.first_name,
                "weight": penalty.weight,
                "event": penalty.source_event.title,
                "reason": penalty.reason,
            },
            subject="Du har fått en ny prikk",
            plain_template="users/email/penalty.txt",
            html_template="users/email/penalty.html",
        )

    def generate_push(self):
        penalty = self.kwargs["penalty"]

        return self._delay_push(
            template="users/push/penalty.txt",
            context={"weight": penalty.weight, "event": penalty.source_event.title},
            instance=penalty,
        )


class InactiveNotification(Notification):

    name = INACTIVE_WARNING

    def generate_mail(self):
        max_inactive_days = self.kwargs["max_inactive_days"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "name": self.user.full_name,
                "username": self.user.username,
                "last_login": str(self.user.last_login.date()),
                "date_of_deletion": str(
                    (self.user.last_login + timedelta(max_inactive_days)).date()
                ),
            },
            subject="Du har vært inaktiv lenge",
            plain_template="users/email/inactive.txt",
            html_template="users/email/inactive.html",
        )


class DeletedUserNotification(Notification):

    name = DELETED_WARNING

    def generate_mail(self):

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "name": self.user.full_name,
                "username": self.user.username,
            },
            subject="Din bruker har blitt slettet",
            plain_template="users/email/deleted.txt",
            html_template="users/email/deleted.html",
        )
