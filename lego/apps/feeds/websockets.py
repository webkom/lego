from __future__ import annotations

from typing import TYPE_CHECKING

from lego.apps.feeds.serializers.sockets import FeedActivitySocketSerializer
from lego.apps.websockets.groups import group_for_user
from lego.apps.websockets.notifiers import notify_group

if TYPE_CHECKING:
    from lego.apps.feeds.models import NotificationFeed


def notify_new_notification(aggregated_activity: NotificationFeed):
    from lego.apps.feeds.views import FeedViewSet

    group = group_for_user(aggregated_activity.feed_id)
    serializer = FeedActivitySocketSerializer(
        {
            "type": "SOCKET_NEW_NOTIFICATION",
            "payload": aggregated_activity,
        }
    )
    data = serializer.data
    data["payload"] = FeedViewSet.attach_metadata([data["payload"]])[0]
    notify_group(group, data)
