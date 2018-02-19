from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.fanout_manager import fanout_manager
from lego.apps.feeds.models import NotificationFeed, PersonalFeed
from lego.apps.feeds.verbs import AnnouncementVerb
from lego.apps.notifications.models import Announcement
from lego.apps.notifications.notifications import AnnouncementNotification


class AnnouncementHandler(Handler):

    model = Announcement
    manager = fanout_manager

    def handle_send(self, announcement):
        if not announcement.created_by:
            return

        activity = Activity(
            actor=announcement.created_by, verb=AnnouncementVerb, object=announcement,
            time=announcement.created_at, extra_context={}
        )
        recipients = announcement.lookup_recipients()
        self.manager.add_activity(
            activity,
            [recipient.pk for recipient in recipients],
            [NotificationFeed, PersonalFeed]
        )

        # Send notifications
        for recipient in recipients:
            notification = AnnouncementNotification(recipient, announcement=announcement)
            notification.notify()


register_handler(AnnouncementHandler)
