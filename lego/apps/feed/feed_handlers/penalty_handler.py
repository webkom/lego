from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import PenaltyVerb
from lego.apps.users.models import Penalty
from lego.apps.users.notifications import PenaltyNotification


class PenaltyHandler(BaseHandler):
    model = Penalty
    manager = feed_manager

    def get_activity(self, penalty):
        return Activity(
            actor=penalty.source_event,
            verb=PenaltyVerb,
            object=penalty,
            target=penalty.user,
            time=penalty.created_at,
            extra_context={
                'reason': penalty.reason,
                'weight': penalty.weight,
                'total': penalty.user.number_of_penalties()
            }
        )

    def handle_create(self, penalty):
        activity = self.get_activity(penalty)
        self.manager.add_activity(activity, [penalty.user.pk], [NotificationFeed])

        # Send Notification
        notification = PenaltyNotification(penalty.user, penalty=penalty)
        notification.notify()

    def handle_update(self, penalty):
        activity = self.get_activity(penalty)
        self.manager.add_activity(activity, [penalty.user.pk], [NotificationFeed])

    def handle_delete(self, penalty):
        activity = self.get_activity(penalty)
        self.manager.remove_activity(activity, [penalty.user.pk], [NotificationFeed])


register_handler(PenaltyHandler)
