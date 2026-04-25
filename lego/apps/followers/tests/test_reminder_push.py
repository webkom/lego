from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from lego.apps.events.models import Pool
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.followers.notifications import RegistrationReminderNotification
from lego.apps.users.models import AbakusGroup
from lego.utils.content_types import instance_to_string
from lego.utils.test_utils import BaseTestCase


@patch("lego.apps.notifications.notification.send_push.delay")
class RegistrationReminderPushTestCase(BaseTestCase):
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

    def assertPushEquals(self, send_push_mock, key, value):
        self.notifier.generate_push()
        push_args = send_push_mock.call_args[1]
        self.assertEqual(push_args[key], value)

    def test_generate_push_event(self, send_push_mock):
        self.assertPushEquals(
            send_push_mock, "context", {"event": self.pool.event.title}
        )

    def test_generate_push_target(self, send_push_mock):
        self.assertPushEquals(
            send_push_mock, "target", instance_to_string(self.pool.event)
        )

    def test_generate_push_template(self, send_push_mock):
        self.assertPushEquals(send_push_mock, "template", "followers/push/reminder.txt")

    def test_generate_push_title(self, send_push_mock):
        self.assertPushEquals(send_push_mock, "title", "Påmelding til arrangement")
