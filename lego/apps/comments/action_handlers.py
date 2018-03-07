from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.comments.models import Comment
from lego.apps.comments.notifications import CommentNotification, CommentReplyNotification
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed, PersonalFeed, UserFeed
from lego.apps.feeds.verbs import CommentReplyVerb, CommentVerb


class CommentHandler(Handler):
    model = Comment
    manager = feed_manager

    def get_activity(self, comment, reply=False):
        return Activity(
            actor=comment.created_by, verb=CommentReplyVerb
            if reply else CommentVerb, object=comment, target=comment.content_object,
            time=comment.created_at, extra_context={'content': comment.text}
        )

    def handle_create(self, instance, **kwargs):
        activity = self.get_activity(instance)
        author = instance.created_by
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.add_activity(activity, [recipient.pk for recipient in recipients], feeds)
            if NotificationFeed in feeds:
                for recipient in recipients:
                    notification = CommentNotification(
                        user=recipient, target=instance.content_object, author=author,
                        text=instance.text
                    )
                    notification.notify()

        if instance.parent and instance.parent.created_by != author:
            parent_author = instance.parent.created_by
            reply_activity = self.get_activity(instance, reply=True)
            self.manager.add_activity(reply_activity, [parent_author.pk], [NotificationFeed])
            reply_notification = CommentReplyNotification(
                user=parent_author, target=instance.content_object, author=author
            )
            reply_notification.notify()

    def handle_delete(self, instance, **kwargs):
        activity = self.get_activity(instance)
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.remove_activity(
                activity,
                [recipient.pk for recipient in recipients], feeds
            )

    def get_feeds_and_recipients(self, comment):
        result = []
        if hasattr(comment.content_object, 'followers'):
            author = comment.created_by
            followers = comment.content_object.followers.all().select_related('follower')
            result.append(
                (
                    [PersonalFeed, NotificationFeed],
                    [follow.follower for follow in followers if not follow.follower == author]
                )
            )

        if comment.created_by:
            result.append(([UserFeed], [comment.created_by]))
        return result


register_handler(CommentHandler)
