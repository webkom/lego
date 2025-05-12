from lego.apps.action_handlers.handler import Handler
from lego.apps.action_handlers.registry import register_handler
from lego.apps.comments.models import Comment
from lego.apps.comments.notifications import CommentReplyNotification
from lego.apps.comments.constants import SOCKET_ADD_SUCCESS, SOCKET_DELETE_SUCCESS
from lego.apps.comments.websockets import notify_comment
from lego.apps.feeds.activity import Activity
from lego.apps.feeds.feed_manager import feed_manager
from lego.apps.feeds.models import NotificationFeed, UserFeed
from lego.apps.feeds.verbs import CommentReplyVerb, CommentVerb
from lego.apps.permissions.models import ObjectPermissionsModel


class CommentHandler(Handler):
    model = Comment
    manager = feed_manager

    @staticmethod
    def get_activity(comment, reply=False):
        return Activity(
            actor=comment.created_by,
            verb=CommentReplyVerb if reply else CommentVerb,
            object=comment,
            target=comment.content_object,
            time=comment.created_at,
            extra_context={"content": comment.text},
        )

    def handle_create(self, instance, **kwargs):
        activity = self.get_activity(instance)
        author = instance.created_by
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.add_activity(
                activity, [recipient.pk for recipient in recipients], feeds
            )

        if instance.parent and instance.parent.created_by != author:
            parent_author = instance.parent.created_by
            reply_activity = self.get_activity(instance, reply=True)
            self.manager.add_activity(
                reply_activity, [parent_author.pk], [NotificationFeed]
            )
            reply_notification = CommentReplyNotification(
                user=parent_author,
                text=instance.text,
                target=instance.content_object,
                author=author,
            )
            reply_notification.notify()
        
        notify_comment(SOCKET_ADD_SUCCESS, instance)

    def handle_delete(self, instance, **kwargs):
        notify_comment(SOCKET_DELETE_SUCCESS, instance)
        if not (
            isinstance(instance.parent, ObjectPermissionsModel)
            and not instance.parent.require_auth
        ):
            return

        activity = self.get_activity(instance)
        for feeds, recipients in self.get_feeds_and_recipients(instance):
            self.manager.remove_activity(
                activity, [recipient.pk for recipient in recipients], feeds
            )
        

    def get_feeds_and_recipients(self, comment):
        result = []

        if comment.created_by:
            result.append(([UserFeed], [comment.created_by]))
        return result


register_handler(CommentHandler)
