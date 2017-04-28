from stream_framework.metrics.statsd import StatsdMetrics

from lego.apps.stats.statsd_client import statsd


class FeedMetrics(StatsdMetrics):

    def __init__(self, *args, **kwargs):
        self.statsd = statsd
