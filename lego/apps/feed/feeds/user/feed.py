from lego.apps.feed.feed import AggregatedFeed


class UserFeed(AggregatedFeed):
    """
    This feeds should contains activities related to a user based on friends, and followed events.
    """

    timeline_cf_name = 'user'
