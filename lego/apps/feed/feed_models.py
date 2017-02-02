from cassandra.cqlengine import columns
from stream_framework.storage.cassandra import models as feed_models


class AggregatedActivityModel(feed_models.AggregatedActivity):
    """
    Custom cassandra model for aggregated activities.
    """
    minimized_activities = columns.Integer(required=False)
