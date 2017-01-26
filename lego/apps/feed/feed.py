from stream_framework.feeds.aggregated_feed.cassandra import CassandraAggregatedFeed
from stream_framework.feeds.notification_feed.base import BaseNotificationFeed
from stream_framework.storage.redis.lists_storage import RedisListsStorage

from lego.apps.feed.activities import Activity, AggregatedActivity, NotificationActivity
from lego.apps.feed.aggregator import FeedAggregator
from lego.apps.feed.feed_models import AggregatedActivityModel
from lego.apps.feed.feed_serializers import AggregatedActivitySerializer


class AggregatedFeed(CassandraAggregatedFeed):
    """
    Aggregated feed. Group activities by type.
    Usage:
    * Set the column_family used to store the feed in cassandra
      timeline_cf_name = ''
    """
    key_format = '%(user_id)s'
    timeline_model = AggregatedActivityModel
    timeline_serializer = AggregatedActivitySerializer
    aggregator_class = FeedAggregator
    activity_class = Activity
    aggregated_activity_class = AggregatedActivity


class NotificationFeed(BaseNotificationFeed, AggregatedFeed):
    """
    Track read/seen states on an aggregated feed.
    """
    markers_storage_class = RedisListsStorage
    aggregated_activity_class = NotificationActivity
