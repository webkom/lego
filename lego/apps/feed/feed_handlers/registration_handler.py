from lego.apps.events.models import Registration
from lego.apps.events.notifications import (EventAdminRegistrationNotification,
                                            EventBumpNotification, EventPaymentOverdueNotification)
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import (AdminRegistrationVerb, EventRegisterVerb, PaymentOverdueVerb,
                                  RegistrationBumpVerb)


class RegistrationHandler(BaseHandler):
    model = Registration
    manager = feed_manager

    def handle_create(self, registration):
        activity = self.get_activity(registration)
        for feeds, recipients in self.get_feeds_and_recipients(registration):
            self.manager.add_activity(
                activity, recipients, feeds
            )

    def handle_update(self, registration):
        registered = registration.unregistration_date is not None
        if registered:
            feed_function = self.manager.add_activity
        else:
            feed_function = self.manager.remove_activity

        if registration.unregistration_date is not None:
            activity = self.get_activity(registration)
            for feeds, recipients in self.get_feeds_and_recipients(registration):
                feed_function(
                    activity, recipients, feeds
                )

    def handle_delete(self, registration):
        activity = self.get_activity(registration)
        for feeds, recipients in self.get_feeds_and_recipients(registration):
            self.manager.remove_activity(
                activity, recipients, feeds
            )

    def get_activity(self, registration):
        return Activity(
            verb=EventRegisterVerb,
            actor=registration.user,
            target=registration.event,
            object=registration,
            time=registration.created_at,
            extra_context={}
        )

    def get_feeds_and_recipients(self, registration):
        result = []

        followers = registration.user.followers \
            .exclude(follower_id=registration.user_id) \
            .values_list('follower_id', flat=True)

        result.append(([PersonalFeed], followers))
        result.append(([UserFeed], [registration.user_id]))
        return result

    def handle_payment_overdue(self, registration):
        """
        Notify about payment overdue, called from a celery task run by beat.
        """
        activity = Activity(
            actor=registration.event,
            verb=PaymentOverdueVerb,
            object=registration,
            target=registration.user,
        )
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

        # Send notification
        notification = EventPaymentOverdueNotification(registration.user, event=registration.event)
        notification.notify()

    def handle_bump(self, registration):
        activity = Activity(
            actor=registration.event,
            verb=RegistrationBumpVerb,
            object=registration,
            target=registration.user
        )
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

        # Send Notification
        notification = EventBumpNotification(
            registration.user, event=registration.event
        )
        notification.notify()

    def handle_admin_registration(self, registration):
        activity = Activity(
            actor=registration.event,
            verb=AdminRegistrationVerb,
            object=registration,
            target=registration.user
        )
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

        # Send Notification
        notification = EventAdminRegistrationNotification(
            registration.user, event=registration.event, reason=registration.admin_reason
        )
        notification.notify()


register_handler(RegistrationHandler)
