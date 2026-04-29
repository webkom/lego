from unittest.mock import patch

from expo_notifications.models import Device, Message

from lego.apps.users.models import User
from lego.utils.push import PushMessage
from lego.utils.test_utils import BaseTestCase


class PushMessageTestCase(BaseTestCase):
    fixtures = ["test_users.yaml"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.sender = User.objects.get(pk=2)
        self.push_message = PushMessage(
            user=self.user,
            template="notifications/push/announcement.txt",
            context={"sender": self.sender.first_name},
            title=f"Kunngjøring fra {self.sender.first_name}",
        )

    @patch("expo_notifications.tasks.send_messages.delay_on_commit")
    def test_send_expo_push_notification(
        self,
        delay_on_commit_mock,
    ):
        expo_device = Device.objects.create(
            user=self.user, push_token="ExponentPushToken[test_token]"
        )
        self.push_message.send()

        expo_message = Message.objects.get(device=expo_device)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(
            expo_message.title, f"Kunngjøring fra {self.sender.first_name}"
        )
        self.assertEqual(
            expo_message.body,
            f"Du har mottatt en kunngjøring fra {self.sender.first_name}.",
        )
        delay_on_commit_mock.assert_called_once_with([expo_message.pk])

    @patch("expo_notifications.tasks.send_messages.delay_on_commit")
    def test_doesnt_send_when_none_expo_device(
        self,
        delay_on_commit_mock,
    ):

        self.push_message.send()
        self.assertEqual(Message.objects.count(), 0)
        delay_on_commit_mock.assert_not_called()
