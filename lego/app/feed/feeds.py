from stream_framework.feeds.notification_feed.redis import RedisNotificationFeed

from .activities import FeedActivity, FeedAggregatedActivity
from .aggregator import FeedAggregator
from .feed_serializers import AggregatedFeedSerializer


class NotificationFeed(RedisNotificationFeed):
    """
    The notification feed is special, normally we use a Feed or AggregatedFeed.
    The notification feed has support for seen and clicked activities.
    """
    key_format = 'feed:notification:%(user_id)s'
    markers_key_format = 'feed:notification:%(user_id)s'
    lock_format = 'feed:notification:%s:lock'

    aggregator_class = FeedAggregator
    activity_class = FeedActivity
    aggregated_activity_class = FeedAggregatedActivity
    timeline_serializer = AggregatedFeedSerializer
