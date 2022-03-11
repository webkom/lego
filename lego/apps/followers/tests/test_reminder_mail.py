from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.utils import timezone

from lego.apps.events.models import Pool
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.followers.notifications import RegistrationReminderNotification
from lego.apps.users.models import AbakusGroup
from lego.utils.test_utils import BaseTestCase


@patch("lego.utils.email.django_send_mail")
class RegistrationReminderTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
        "test_companies.yaml",
        "test_events.yaml",
    ]

    def setUp(self):
        Pool.objects.all().update(
            activation_date=timezone.now() + timedelta(hours=2), name="Webkom"
        )
        self.recipient = get_dummy_users(1)[0]
        AbakusGroup.objects.get(name="Webkom").add_user(self.recipient)
        self.pool = Pool.objects.first()
        self.notifier = RegistrationReminderNotification(
            self.recipient, event=self.pool.event
        )

    def assertEmailContains(self, send_mail_mock, content):
        self.notifier.generate_mail()
        email_args = send_mail_mock.call_args[1]
        self.assertIn(content, email_args["message"])
        self.assertIn(content, email_args["html_message"])

    def test_generate_email_name(self, send_mail_mock):
        opening = "Hei, " + self.recipient.first_name + "!"
        self.assertEmailContains(send_mail_mock, opening)

    def test_generate_email_event(self, send_mail_mock):
        event = (
            "Nå er det under en time til påmelding til "
            + str(self.pool.event.title)
            + " starter."
        )
        self.assertEmailContains(send_mail_mock, event)

    def test_generate_email_url(self, send_mail_mock):
        url = settings.FRONTEND_URL + "/events/" + str(self.pool.event.id)
        self.assertEmailContains(send_mail_mock, url)
