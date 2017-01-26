from lego.apps.feed.feed import AggregatedFeed


class UserFeed(AggregatedFeed):
    timeline_cf_name = 'user'
