from datetime import timedelta
from unittest import mock

from django.utils import timezone

from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.tests.utils import get_dummy_users
from lego.apps.followers.models import FollowEvent
from lego.apps.followers.notifications import RegistrationReminderNotification
from lego.apps.followers.tasks import send_registration_reminder_mail
from lego.apps.users.models import AbakusGroup
from lego.utils.test_utils import BaseTestCase


@mock.patch("lego.apps.followers.tasks.RegistrationReminderNotification.notify")
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
        self.recipient, self.bedkom_member, self.outsider = get_dummy_users(3)
        AbakusGroup.objects.get(name="Webkom").add_user(self.recipient)
        AbakusGroup.objects.get(name="Bedkom").add_user(self.bedkom_member)
        self.pool = Pool.objects.first()
        self.notifier = RegistrationReminderNotification(
            self.recipient, event=self.pool.event
        )

    def create_staggered_event(self):
        """
        An event whose two pools belong to disjoint groups, as when registration
        opens at different times for different classes.
        """
        event = Event.objects.get(title="POOLS_NO_REGISTRATIONS")
        webkom_pool, bedkom_pool = event.pools.order_by("id")
        webkom_pool.permission_groups.set([AbakusGroup.objects.get(name="Webkom")])
        bedkom_pool.permission_groups.set([AbakusGroup.objects.get(name="Bedkom")])
        return event, webkom_pool, bedkom_pool

    def test_follows_registration_under_one_hour(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time + timedelta(minutes=45)
        self.pool.save()
        FollowEvent.objects.get_or_create(
            follower=self.recipient, target=self.pool.event
        )
        send_registration_reminder_mail.delay()
        mock_notification.assert_called()

    def test_follows_registration_over_one_hour(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time + timedelta(minutes=75)
        self.pool.save()
        FollowEvent.objects.get_or_create(
            follower=self.recipient, target=self.pool.event
        )
        send_registration_reminder_mail.delay()
        mock_notification.assert_not_called()

    def test_not_follows_registration_under_one_hour(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time + timedelta(minutes=45)
        self.pool.save()

        send_registration_reminder_mail.delay()
        mock_notification.assert_not_called()

    def test_follows_registration_under_one_hour_already_sent(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time + timedelta(minutes=45)
        self.pool.save()
        FollowEvent.objects.get_or_create(
            follower=self.recipient, target=self.pool.event, notification_sent=True
        )

        send_registration_reminder_mail.delay()
        mock_notification.assert_not_called()

    def test_follows_and_is_registred_under_one_hour(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time + timedelta(minutes=45)
        self.pool.save()
        FollowEvent.objects.get_or_create(
            follower=self.recipient, target=self.pool.event
        )
        Registration.objects.get_or_create(
            pool=self.pool, user=self.recipient, event=self.pool.event
        )

        send_registration_reminder_mail.delay()
        mock_notification.assert_not_called()

    def test_follows_and_is_waiting_list_under_one_hour(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time + timedelta(minutes=45)
        self.pool.save()
        FollowEvent.objects.get_or_create(
            follower=self.recipient, target=self.pool.event
        )
        Registration.objects.get_or_create(
            pool=None, user=self.recipient, event=self.pool.event
        )

        send_registration_reminder_mail.delay()
        mock_notification.assert_not_called()

    def test_follows_registration_past(self, mock_notification):
        current_time = timezone.now()
        self.pool.activation_date = current_time - timedelta(minutes=15)
        self.pool.save()
        FollowEvent.objects.get_or_create(
            follower=self.recipient, target=self.pool.event
        )
        send_registration_reminder_mail.delay()
        mock_notification.assert_not_called()

    def test_follower_of_later_pool_is_reminded_when_their_own_pool_opens(
        self, mock_notification
    ):
        """
        A follower without access to the pool opening first must stay unmarked,
        so they are still reminded when the pool they can join opens.
        """
        event, webkom_pool, bedkom_pool = self.create_staggered_event()
        webkom_pool.activation_date = timezone.now() + timedelta(minutes=45)
        webkom_pool.save()
        webkom_follow = FollowEvent.objects.create(
            follower=self.recipient, target=event
        )
        bedkom_follow = FollowEvent.objects.create(
            follower=self.bedkom_member, target=event
        )

        send_registration_reminder_mail.delay()

        self.assertEqual(mock_notification.call_count, 1)
        webkom_follow.refresh_from_db()
        bedkom_follow.refresh_from_db()
        self.assertTrue(webkom_follow.notification_sent)
        self.assertFalse(bedkom_follow.notification_sent)

        bedkom_pool.activation_date = timezone.now() + timedelta(minutes=45)
        bedkom_pool.save()

        send_registration_reminder_mail.delay()

        self.assertEqual(mock_notification.call_count, 2)
        bedkom_follow.refresh_from_db()
        self.assertTrue(bedkom_follow.notification_sent)

    def test_reminds_followers_of_every_pool_opening_in_the_same_window(
        self, mock_notification
    ):
        event, _, _ = self.create_staggered_event()
        event.pools.all().update(activation_date=timezone.now() + timedelta(minutes=45))
        webkom_follow = FollowEvent.objects.create(
            follower=self.recipient, target=event
        )
        bedkom_follow = FollowEvent.objects.create(
            follower=self.bedkom_member, target=event
        )

        send_registration_reminder_mail.delay()

        self.assertEqual(mock_notification.call_count, 2)
        webkom_follow.refresh_from_db()
        bedkom_follow.refresh_from_db()
        self.assertTrue(webkom_follow.notification_sent)
        self.assertTrue(bedkom_follow.notification_sent)

    def test_follower_without_access_to_any_pool_is_not_marked(self, mock_notification):
        event, _, _ = self.create_staggered_event()
        event.pools.all().update(activation_date=timezone.now() + timedelta(minutes=45))
        follow = FollowEvent.objects.create(follower=self.outsider, target=event)

        send_registration_reminder_mail.delay()

        mock_notification.assert_not_called()
        follow.refresh_from_db()
        self.assertFalse(follow.notification_sent)
