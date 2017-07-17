from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import AnnouncementVerb
from lego.apps.notifications.models import Announcement
from lego.apps.notifications.notifications import AnnouncementNotification


class AnnouncementHandler(BaseHandler):

    model = Announcement
    manager = feed_manager

    def handle_create(self, announcement):
        pass

    def handle_update(self, announcement):
        pass

    def handle_delete(self, announcement):
        pass

    def handle_send(self, announcement):
        if not announcement.created_by:
            return

        activity = Activity(
            actor=announcement.created_by,
            verb=AnnouncementVerb,
            object=announcement,
            time=announcement.created_at,
            extra_context={}
        )
        recipients = announcement.lookup_recipients()
        self.manager.add_activity(
            activity, [recipient.pk for recipient in recipients], [NotificationFeed, PersonalFeed]
        )

        # Send notifications
        for recipient in recipients:
            notification = AnnouncementNotification(
                recipient, announcement=announcement
            )
            notification.notify()


register_handler(AnnouncementHandler)
