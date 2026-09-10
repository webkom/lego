from __future__ import annotations

from typing import TYPE_CHECKING

from lego.apps.feeds.attr_cache import AttrCache
from lego.apps.feeds.context import collect_refs
from lego.apps.feeds.serializers.sockets import FeedActivitySocketSerializer
from lego.apps.websockets.groups import group_for_user
from lego.apps.websockets.notifiers import notify_group

if TYPE_CHECKING:
    from lego.apps.feeds.models import NotificationFeed


def notify_new_notification(aggregated_activity: NotificationFeed):
    refs = collect_refs(aggregated_activity)
    lookup = AttrCache().bulk_lookup(refs) if refs else {}

    group = group_for_user(aggregated_activity.feed_id)
    serializer = FeedActivitySocketSerializer(
        {
            "type": "SOCKET_NEW_NOTIFICATION",
            "payload": aggregated_activity,
        },
        context={"attr_lookup": lookup},
    )
    data = serializer.data
    notify_group(group, data)
