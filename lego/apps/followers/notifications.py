from lego.apps.notifications.constants import PENALTY_CREATION
from lego.apps.notifications.notification import Notification


class PenaltyTest(Notification):

    name = PENALTY_CREATION

    def generate_mail(self):
        penalty = self.kwargs["penalty"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "name": self.user.full_name,
                "event": penalty.source_event.title,
                "event_id": penalty.source_event.id,
            },
            subject=f"Påminnelse",
            plain_template="users/email/penalty.txt",
            html_template="users/email/test.html",
        )

    def generate_push(self):
        penalty = self.kwargs["penalty"]

        return self._delay_push(
            template="users/push/penalty.txt",
            context={"weight": penalty.weight,
                     "event": penalty.source_event.title},
            instance=penalty,
        )
