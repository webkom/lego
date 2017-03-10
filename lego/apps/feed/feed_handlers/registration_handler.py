from django.utils import timezone

from lego.apps.events.models import Registration
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import RegistrationBumpVerb


class RegistrationHandler(BaseHandler):
    model = Registration

    manager = feed_manager

    def handle_create(self, registration):
        pass

    def handle_bump(self, registration):
        activity = self.get_activity(registration, 'bump')
        self.manager.add_activity(activity, [registration.user_id], [NotificationFeed])

    def handle_update(self, registration):

        pass

    def handle_delete(self, registration):
        pass

    def get_feeds_and_recipients(self, registration):
        pass

    def get_activity(self, registration, verb_key):
        verbs = {
            'bump': RegistrationBumpVerb,
        }

        return Activity(
            actor=registration.event,
            verb=verbs.get(verb_key),
            object=registration,
            time=timezone.now()
        )


register_handler(RegistrationHandler)