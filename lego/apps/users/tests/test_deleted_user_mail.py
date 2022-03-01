from unittest.mock import patch

from django.conf import settings

from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.notifications import DeletedUserNotification
from lego.apps.users.tasks import MAX_INACTIVE_DAYS
from lego.utils.test_utils import BaseTestCase


@patch("lego.utils.email.django_send_mail")
class DeletedUserNotificationTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        self.recipient = get_dummy_users(1)[0]
        self.notifier = DeletedUserNotification(
            self.recipient, max_inactive_days=MAX_INACTIVE_DAYS
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["message"])
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_name(self, send_mail_mock):
        opening = f"Hei {self.recipient.first_name}!"
        self.assertEmailContains(send_mail_mock, opening)

    def test_generate_max_inactive_days(self, send_mail_mock):
        max_days = f"Du har ikke logget inn på over {MAX_INACTIVE_DAYS} dager."
        self.assertEmailContains(send_mail_mock, max_days)

    def test_generate_email_username(self, send_mail_mock):
        username_deleteion = (
            f"Brukeren din; {self.recipient.username}, har blitt slettet grunnet GDPR."
        )
        self.assertEmailContains(send_mail_mock, username_deleteion)

    def test_generate_email_url(self, send_mail_mock):
        url = settings.FRONTEND_URL
        self.assertEmailContains(send_mail_mock, url)
