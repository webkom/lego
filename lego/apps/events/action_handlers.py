from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.events.models import Event, Registration
from lego.apps.events.notifications import (
    EventAdminRegistrationNotification, EventAdminUnregistrationNotification, EventBumpNotification,
    EventPaymentOverdueNotification
)
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed, PersonalFeed, UserFeed
from lego.apps.feeds.verbs import (
    AdminRegistrationVerb, AdminUnregistrationVerb, EventCreateVerb, EventRegisterVerb,
    PaymentOverdueVerb, RegistrationBumpVerb
)


class EventHandler(Handler):

    model = Event
    manager = feed_manager

    def handle_create(self, instance, **kwargs):
        activity = self.get_activity(instance)
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.add_activity(activity, recipients, feeds)

    def handle_update(self, instance, **kwargs):
        pass

    def handle_delete(self, instance, **kwargs):
        activity = self.get_activity(instance)
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.remove_activity(activity, recipients, feeds)

    def get_feeds_and_recipients(self, event):
        result = []
        if event.company_id:
            result.append(
                (
                    [PersonalFeed],
                    list(event.company.followers.values_list('follower__id', flat=True))
                )
            )
        return result

    def get_activity(self, event):
        return Activity(
            actor=event.company, verb=EventCreateVerb, object=event, time=event.created_at,
            extra_context={'title': event.title}
        )


register_handler(EventHandler)


class RegistrationHandler(Handler):

    model = Registration
    manager = feed_manager

    def handle_create(self, instance, **kwargs):
        activity = self.get_activity(instance)
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.add_activity(activity, recipients, feeds)

    def handle_update(self, instance, **kwargs):
        registered = instance.unregistration_date is not None
        if registered:
            feed_function = self.manager.add_activity
        else:
            feed_function = self.manager.remove_activity

        if instance.unregistration_date is not None:
            activity = self.get_activity(instance)
            for feeds, recipients in self.get_feeds_and_recipients(instance):
                feed_function(activity, recipients, feeds)

    def handle_delete(self, instance, **kwargs):
        activity = self.get_activity(instance)
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.remove_activity(activity, recipients, feeds)

    def get_activity(self, registration):
        return Activity(
            verb=EventRegisterVerb, actor=registration.user, target=registration.event,
            object=registration, time=registration.created_at, extra_context={}
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
            actor=registration.event, verb=RegistrationBumpVerb, object=registration,
            target=registration.user
        )
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

        # Send Notification
        notification = EventBumpNotification(registration.user, event=registration.event)
        notification.notify()

    def handle_admin_registration(self, registration):
        activity = Activity(
            actor=registration.event, verb=AdminRegistrationVerb, object=registration,
            target=registration.user
        )
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

        # Send Notification
        notification = EventAdminRegistrationNotification(
            registration.user, event=registration.event,
            reason=registration.admin_registration_reason
        )
        notification.notify()

    def handle_admin_unregistration(self, registration):
        activity = Activity(
            actor=registration.event, verb=AdminUnregistrationVerb, object=registration,
            target=registration.user
        )
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

        # Send Notification
        notification = EventAdminUnregistrationNotification(
            registration.user, event=registration.event,
            reason=registration.admin_unregistration_reason, creator=registration.event.created_by
        )
        notification.notify()


register_handler(RegistrationHandler)
