from lego.apps.events.models import Registration
from lego.apps.events.notifications import (EventAdminRegistrationNotification,
                                            EventBumpNotification, EventPaymentOverdueNotification)
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import AdminRegistrationVerb, PaymentOverdueVerb, RegistrationBumpVerb


class RegistrationHandler(BaseHandler):
    model = Registration
    manager = feed_manager

    def handle_create(self, registration):
        pass

    def handle_update(self, registration):
        pass

    def handle_delete(self, registration):
        pass

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
