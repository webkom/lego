from datetime import timedelta
from unittest import mock

from django.utils import timezone

from lego.apps.oauth.models import APIApplication
from lego.apps.users.models import User
from lego.apps.users.tasks import (
    MAX_INACTIVE_DAYS,
    MEDIAN_INACTIVE_DAYS,
    MIN_INACTIVE_DAYS,
    send_inactive_reminder_mail_and_delete_users,
)
from lego.utils.test_utils import BaseTestCase


def make_application_owner(user):
    return APIApplication.objects.create(
        user=user,
        client_type=APIApplication.CLIENT_CONFIDENTIAL,
        authorization_grant_type=APIApplication.GRANT_CLIENT_CREDENTIALS,
        name="machine client",
    )


@mock.patch("lego.apps.users.tasks.InactiveNotification.notify")
class InactiveNotificationTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        User.objects.all().update(last_login=timezone.now())

    def test_all_users_active(self, mock_notification):
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_not_called()

    def test_one_user_monthly_have_not_been_notified(self, mock_notification):
        inactive_user = User.objects.first()
        last_login_date = timezone.now() - timedelta(days=MIN_INACTIVE_DAYS)
        inactive_user.last_login = last_login_date
        inactive_user.save()
        counter_before = inactive_user.inactive_notified_counter
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_called_once()
        inactive_user.refresh_from_db()
        counter_after = inactive_user.inactive_notified_counter
        self.assertEqual(counter_before + 1, counter_after)

    def test_one_user_monthly_have_been_notified(self, mock_notification):
        inactive_user = User.objects.first()
        last_login_date = timezone.now() - timedelta(days=MIN_INACTIVE_DAYS + 7)
        inactive_user.last_login = last_login_date
        inactive_user.inactive_notified_counter = 1
        inactive_user.save()
        counter_before = inactive_user.inactive_notified_counter
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_not_called()
        inactive_user.refresh_from_db()
        counter_after = inactive_user.inactive_notified_counter
        self.assertEqual(counter_before, counter_after)

    def test_application_owner_is_not_notified(self, mock_notification):
        inactive_owner = User.objects.first()
        make_application_owner(inactive_owner)
        inactive_owner.last_login = timezone.now() - timedelta(days=MIN_INACTIVE_DAYS)
        inactive_owner.save()
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_not_called()

    def test_one_user_weekly(self, mock_notification):
        inactive_user = User.objects.first()
        last_login_date = timezone.now() - timedelta(days=MEDIAN_INACTIVE_DAYS)
        inactive_user.last_login = last_login_date
        inactive_user.inactive_notified_counter = 1
        inactive_user.save()
        counter_before = inactive_user.inactive_notified_counter
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_called_once()
        inactive_user.refresh_from_db()
        counter_after = inactive_user.inactive_notified_counter
        self.assertEqual(counter_before + 1, counter_after)

    def test_one_user_max_inactive_single_notification(self, mock_notification):
        num_users_before = len(User.objects.all())
        inactive_user = User.objects.first()
        last_login_date = timezone.now() - timedelta(days=2 * MAX_INACTIVE_DAYS)
        inactive_user.last_login = last_login_date
        inactive_user.inactive_notified_counter = 1
        inactive_user.save()
        counter_before = inactive_user.inactive_notified_counter
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_called_once()
        inactive_user.refresh_from_db()
        counter_after = inactive_user.inactive_notified_counter
        self.assertEqual(counter_before + 1, counter_after)
        num_users_after = len(User.objects.all())
        self.assertEqual(num_users_before, num_users_after)


@mock.patch("lego.apps.users.tasks.DeletedUserNotification.notify")
class DeletedUserNotificationTestCase(BaseTestCase):
    fixtures = [
        "test_abakus_groups.yaml",
        "test_users.yaml",
    ]

    def setUp(self):
        User.objects.all().update(last_login=timezone.now())

    def test_application_owner_is_never_deleted(self, mock_notification):
        num_users_before = User.objects.count()
        inactive_owner = User.objects.first()
        application = make_application_owner(inactive_owner)
        inactive_owner.last_login = timezone.now() - timedelta(
            days=2 * MAX_INACTIVE_DAYS
        )
        inactive_owner.inactive_notified_counter = 5
        inactive_owner.save()
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_not_called()
        self.assertEqual(num_users_before, User.objects.count())
        self.assertTrue(APIApplication.objects.filter(pk=application.pk).exists())

    def test_one_user_to_be_deleted(self, mock_notification):
        num_users_before = len(User.objects.all())
        inactive_user = User.objects.first()
        last_login_date = timezone.now() - timedelta(days=MAX_INACTIVE_DAYS)
        inactive_user.last_login = last_login_date
        inactive_user.inactive_notified_counter = 5
        inactive_user.save()
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_called()
        num_users_after = len(User.objects.all())
        self.assertNotEqual(num_users_before, num_users_after)

    def test_one_user_max_inactive_single_notification(self, mock_notification):
        num_users_before = len(User.objects.all())
        inactive_user = User.objects.first()
        last_login_date = timezone.now() - timedelta(days=2 * MAX_INACTIVE_DAYS)
        inactive_user.last_login = last_login_date
        inactive_user.inactive_notified_counter = 1
        inactive_user.save()
        counter_before = inactive_user.inactive_notified_counter
        send_inactive_reminder_mail_and_delete_users.delay()
        mock_notification.assert_not_called()
        inactive_user.refresh_from_db()
        counter_after = inactive_user.inactive_notified_counter
        self.assertEqual(counter_before + 1, counter_after)
        num_users_after = len(User.objects.all())
        self.assertEqual(num_users_before, num_users_after)
