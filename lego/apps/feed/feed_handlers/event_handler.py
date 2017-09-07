from lego.apps.events.models import Event
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.company_feed import CompanyFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import EventCreateVerb


class EventHandler(BaseHandler):
    model = Event
    manager = feed_manager

    def handle_create(self, event):
        activity = self.get_activity(event)
        for feeds, recipients in self.get_feeds_and_recipients(event):
            self.manager.add_activity(activity, recipients, feeds)

    def handle_update(self, event):
        pass

    def handle_delete(self, event):
        activity = self.get_activity(event)
        for feeds, recipients in self.get_feeds_and_recipients(event):
            self.manager.remove_activity(activity, recipients, feeds)

    def get_feeds_and_recipients(self, event):
        result = []
        if event.company_id:
            result.append((
                [PersonalFeed],
                list(event.company.followers.values_list('follower__id', flat=True))
            ))
            result.append(([CompanyFeed], [event.company_id]))
        return result

    def get_activity(self, event):
        return Activity(
            actor=event.company,
            verb=EventCreateVerb,
            object=event,
            time=event.created_at,
            extra_context={
                'title': event.title
            }
        )


register_handler(EventHandler)
