from lego.apps.action_handlers import registry
from lego.apps.action_handlers.handler import Handler
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed
from lego.apps.feeds.verbs import RestrictedMailSent
from lego.apps.restricted.models import RestrictedMail
from lego.apps.restricted.notifications import RestrictedMailSentNotification
from lego.utils.tasks import send_email


class RestrictedHandler(Handler):

    model = RestrictedMail
    manager = feed_manager

    def handle_sent(self, instance):
        """
        A restricted mail is successfully processed by the system.
        """
        if not instance.created_by:
            return

        activity = Activity(
            actor=instance.created_by, verb=RestrictedMailSent, object=instance, time=instance.used,
            extra_context={}
        )
        self.manager.add_activity(activity, [instance.created_by.pk], [NotificationFeed])

        # Send notification
        notification = RestrictedMailSentNotification(instance.created_by)
        notification.notify()

    def handle_failure(self, sender, reason):
        """
        Notify about restricted mail failure. This action is not connected to a specific user.
        We sends a message to the sender instead of a user. We use the send_mail task directly
        because of this.
        """
        send_email.delay(
            to_email=sender,
            context={'reason': reason},
            subject=f'Kunne ikke sende ut begrenset epost',
            plain_template='restricted/email/process_failure.txt',
            html_template='restricted/email/process_failure.html',
        )


registry.register_handler(RestrictedHandler)
