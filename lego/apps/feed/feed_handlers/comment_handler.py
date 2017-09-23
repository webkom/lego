from lego.apps.comments.models import Comment
from lego.apps.comments.notifications import CommentNotification, CommentReplyNotification
from lego.apps.feed.activities import Activity
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.feed_manager import feed_manager
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import CommentReplyVerb, CommentVerb


class CommentHandler(BaseHandler):
    model = Comment
    manager = feed_manager

    def get_activity(self, comment, reply=False):
        return Activity(
            actor=comment.created_by,
            verb=CommentReplyVerb if reply else CommentVerb,
            object=comment,
            target=comment.content_object,
            time=comment.created_at,
            extra_context={
                'content': comment.text
            }
        )

    def handle_create(self, comment):
        activity = self.get_activity(comment)
        for feeds, recipients in self.get_feeds_and_recipients(comment):
            self.manager.add_activity(activity, [recipient.pk for recipient in recipients], feeds)
            if UserFeed not in feeds:
                for recipient in recipients:
                    notification = CommentNotification(
                        user=recipient, target=comment.content_object, author=comment.created_by
                    )
                    notification.notify()

        if comment.parent:
            parent_author = comment.parent.created_by
            reply_activity = self.get_activity(comment, reply=True)
            self.manager.add_activity(
                reply_activity, [parent_author.pk], [NotificationFeed]
            )
            reply_notification = CommentReplyNotification(
                user=parent_author, target=comment.content_object, author=comment.created_by
            )
            reply_notification.notify()

    def handle_update(self, comment):
        """
        No support for comment updates...
        """
        pass

    def handle_delete(self, comment):
        activity = self.get_activity(comment)
        for feeds, recipients in self.get_feeds_and_recipients(comment):
            self.manager.remove_activity(
                activity, [recipient.pk for recipient in recipients], feeds
            )

    def get_feeds_and_recipients(self, comment):
        result = []
        if hasattr(comment.content_object, 'followers'):
            followers = comment.content_object.followers.all().select_related('follower')
            result.append((
                [PersonalFeed, NotificationFeed],
                [follow.follower for follow in followers]
            ))

        if comment.created_by:
            result.append(([UserFeed], [comment.created_by]))
        return result


register_handler(CommentHandler)
