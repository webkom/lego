from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.utils import timezone

from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.users.notifications import InactiveNotification
from lego.apps.users.tasks import MAX_INACTIVE_DAYS, MIN_INACTIVE_DAYS
from lego.utils.test_utils import BaseTestCase


@patch("lego.utils.email.django_send_mail")
class InactiveNotificationTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        self.recipient = get_dummy_users(1)[0]
        self.recipient.last_login = timezone.now() + timedelta(days=MIN_INACTIVE_DAYS)
        self.recipient.save()
        self.notifier = InactiveNotification(
            self.recipient, max_inactive_days=MAX_INACTIVE_DAYS
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["message"])
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_name(self, send_mail_mock):
        opening = f"Hei {self.recipient.first_name} {self.recipient.last_name}!"
        self.assertEmailContains(send_mail_mock, opening)

    def test_generate_email_last_login(self, send_mail_mock):
        last_login = f"Du har ikke logget inn siden {self.recipient.last_login.date()}."
        self.assertEmailContains(send_mail_mock, last_login)

    def test_generate_email_username_date_of_deletion(self, send_mail_mock):
        last_date_before_deletion = (
            self.recipient.last_login + timedelta(days=MAX_INACTIVE_DAYS)
        ).date()
        username_deleteion = f"Brukeren din; {self.recipient.username}, kan bli slettet etter {last_date_before_deletion}."
        self.assertEmailContains(send_mail_mock, username_deleteion)

    def test_generate_email_url(self, send_mail_mock):
        url = settings.FRONTEND_URL + "/users/me"
        self.assertEmailContains(send_mail_mock, url)
