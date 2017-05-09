from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import RestrictedMailSent
from lego.apps.restricted.models import RestrictedMail
from lego.apps.restricted.notifications import RestrictedMailSentNotification
from lego.utils.tasks import send_email


class RestrictedHandler(BaseHandler):

    model = RestrictedMail
    manager = feed_manager

    def handle_create(self, restricted_mail):
        pass

    def handle_update(self, restricted_mail):
        pass

    def handle_delete(self, restricted_mail):
        pass

    def handle_sent(self, restricted_mail):
        """
        A restricted mail is successfully processed by the system.
        """
        if not restricted_mail.created_by:
            return

        activity = Activity(
            actor=restricted_mail.created_by,
            verb=RestrictedMailSent,
            object=restricted_mail,
            time=restricted_mail.used,
            extra_context={}
        )
        self.manager.add_activity(activity, [restricted_mail.created_by.pk], [NotificationFeed])

        # Send notification
        notification = RestrictedMailSentNotification(
            restricted_mail.created_by
        )
        notification.notify()

    def handle_failure(self, restricted_mail, sender, reason):
        """
        Notify about restricted mail failure. This action is not connected to a specific user.
        We sends a message to the sender instead of a user. We use the send_mail task directly
        because of this.
        """
        send_email.delay(
            to_email=sender,
            context={
                'reason': reason
            },
            subject=f'Kunne ikke sende ut begrenset epost',
            plain_template='restricted/email/process_failure.txt',
            html_template='restricted/email/process_failure.html',
        )


register_handler(RestrictedHandler)
