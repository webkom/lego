from lego.apps.comments.models import Comment
from lego.apps.feed.handlers.base_handler import BaseHandler
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import CommentVerb, DeleteVerb, UpdateVerb


class CommentHandler(BaseHandler):
    verbs = dict(
        create=CommentVerb,
        update=UpdateVerb,
        delete=DeleteVerb
    )

    model = Comment

    @classmethod
    def get_target(cls, instance, action):
        return instance.content_object


register_handler(CommentHandler)
