from lego.apps.comments.models import Comment
from lego.apps.feed.feed_handlers.base_handler import BaseHandler
from lego.apps.feed.registry import register_handler
from lego.apps.feed.verbs import CommentVerb, DeleteVerb, UpdateVerb


class CommentHandler(BaseHandler):
    verbs = dict(
        create=CommentVerb,
        update=UpdateVerb,
        delete=DeleteVerb
    )

    model = Comment

    @property
    def user_ids(self):
        ids = []
        if hasattr(self.target, 'created_by'):
            ids.append(self.target.created_by)

        return ids

    @property
    def target(self):
        return self.instance.content_object


register_handler(CommentHandler)
