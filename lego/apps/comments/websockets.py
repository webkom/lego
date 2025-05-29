from __future__ import annotations

from typing import TYPE_CHECKING

from lego.apps.comments.serializers.sockets import CommentSocketSerializer
from lego.apps.websockets.groups import group_for_content_model
from lego.apps.websockets.notifiers import notify_group

if TYPE_CHECKING:
    from lego.apps.comments.models import Comment


def notify_comment(action_type: str, comment: Comment, **kwargs):
    # group = "global"
    group = group_for_content_model(comment)
    serializer = CommentSocketSerializer(
        {
            "type": action_type,
            "payload": comment,
            "meta": kwargs,
        }
    )
    data = serializer.data
    notify_group(group, data)
