from smtplib import SMTPServerDisconnected
from unittest import mock

from celery.exceptions import Retry
from push_notifications.exceptions import NotificationError

from lego.utils.tasks import send_email, send_push
from lego.utils.test_utils import BaseTestCase

BACKOFF = {"factor": 60, "maximum": 1800, "full_jitter": True}


class SendEmailRetryTestCase(BaseTestCase):
    @mock.patch("lego.utils.tasks.EmailMessage")
    def test_smtp_failure_schedules_a_retry(self, email_mock):
        email_mock.return_value.send.side_effect = SMTPServerDisconnected("busy")

        with mock.patch.object(send_email, "retry", side_effect=Retry) as retry:
            with self.assertRaises(Retry):
                send_email(to_email="test@abakus.no")

        self.assertEqual(retry.call_count, 1)
        self.assertIsInstance(retry.call_args.kwargs["exc"], SMTPServerDisconnected)

    @mock.patch("lego.utils.tasks.EmailMessage")
    def test_retry_delay_scales_in_minutes(self, email_mock):
        email_mock.return_value.send.side_effect = SMTPServerDisconnected("busy")

        with mock.patch(
            "lego.utils.tasks.get_exponential_backoff_interval", return_value=123
        ) as backoff:
            with mock.patch.object(send_email, "retry", side_effect=Retry):
                with self.assertRaises(Retry):
                    send_email(to_email="test@abakus.no")

        backoff.assert_called_once_with(retries=mock.ANY, **BACKOFF)

    @mock.patch("lego.utils.tasks.EmailMessage")
    def test_success_does_not_retry(self, email_mock):
        with mock.patch.object(send_email, "retry", side_effect=Retry) as retry:
            send_email(to_email="test@abakus.no")

        email_mock.return_value.send.assert_called_once()
        retry.assert_not_called()


class SendPushRetryTestCase(BaseTestCase):
    fixtures = ["test_abakus_groups.yaml", "test_users.yaml"]

    @mock.patch("lego.utils.tasks.PushMessage")
    @mock.patch("lego.utils.tasks.User")
    def test_notification_failure_retries_with_the_same_backoff(self, user, push_mock):
        push_mock.return_value.send.side_effect = NotificationError("boom")

        with mock.patch(
            "lego.utils.tasks.get_exponential_backoff_interval", return_value=123
        ) as backoff:
            with mock.patch.object(send_push, "retry", side_effect=Retry) as retry:
                with self.assertRaises(Retry):
                    send_push(user=1, title="t")

        backoff.assert_called_once_with(retries=mock.ANY, **BACKOFF)
        self.assertEqual(retry.call_args.kwargs["countdown"], 123)
