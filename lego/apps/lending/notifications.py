from lego.apps.lending.models import LendingInstance
from lego.apps.notifications.constants import LENDING_INSTANCE_CREATION
from lego.apps.notifications.notification import Notification
from lego.apps.users.models import User


class LendingInstanceCreateNotification(Notification):
    def __init__(self, lending_instance: LendingInstance, user: User):
        self.lending_instance = lending_instance
        self.lender = lending_instance.user

        super().__init__(user=user)

    name = LENDING_INSTANCE_CREATION

    def generate_mail(self):
        return self._delay_mail(
            to_email=self.user.email_address,
            context={
                "lender": self.lender,
                "lendable_object": self.lending_instance.lendable_object.title,
                "start_date": self.lending_instance.start_date,
                "end_date": self.lending_instance.end_date,
            },
            subject="Utlån forespørsel",
            plain_template="users/email/lending_instance.txt",
            html_template="users/email/lending_instance.html",
        )

    def generate_push(self):
        return self._delay_push(
            template="users/push/lending_instance.txt",
            context={
                "lender": self.lender,
                "lendable_object": self.lending_instance.lendable_object.title,
                "start_date": self.lending_instance.start_date,
                "end_date": self.lending_instance.end_date,
            },
            instance=self.lending_instance,
        )
