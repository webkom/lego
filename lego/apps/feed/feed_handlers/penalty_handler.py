from lego.apps.feed.activities import Activity
from lego.apps.feed.feed import NotificationFeed
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import PenaltyCreateVerb
from lego.apps.users.models import Penalty


class PenaltyHandler(BaseHandler):
    model = Penalty

    manager = feed_manager

    def handle_create(self, penalty):
        activity = self.get_activity(penalty)
        feed, recipient = self.get_feeds_and_recipient(penalty)
        self.manager.add_activity(activity, recipient, feed)

    def handle_update(self, penalty):
        pass

    def handle_delete(self, penalty):
        pass

    def get_feeds_and_recipient(self, penalty):
        result = ([NotificationFeed], [penalty.user_id])
        return result

    def get_activity(self, penalty):
        return Activity(
            actor=penalty.source_event,
            verb=PenaltyCreateVerb,
            object=penalty,
            time=penalty.created_at,
            extra_context={
                'reason': penalty.reason,
                'weight': penalty.weight,
                'total_weight': penalty.user.number_of_penalties()
            }
        )


register_handler(PenaltyHandler)
