from lego.apps.comments.models import Comment
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.user.feed import PersonalFeed, UserFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import CommentVerb


class CommentHandler(BaseHandler):
    model = Comment

    manager = feed_manager

    def handle_create(self, comment):
        activity = self.get_activity(comment)
        for feeds, recipients in self.get_feeds_and_recipients(comment):
            self.manager.add_activity(activity, recipients, feeds)

    def handle_update(self, comment):
        pass
        # Update the comment feed entries

    def handle_delete(self, comment):
        activity = self.get_activity(comment)
        for feeds, recipients in self.get_feeds_and_recipients(comment):
            self.manager.remove_activity(activity, recipients, feeds)

    def get_feeds_and_recipients(self, comment):
        return [
            ([PersonalFeed], []),
            ([UserFeed], [comment.created_by.id])
        ]

    def get_activity(self, comment):
        return Activity(
            actor=comment.created_by,
            verb=CommentVerb,
            object=comment,
            target=comment.content_object,
            time=comment.created_at
        )


register_handler(CommentHandler)
