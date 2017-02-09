from prometheus_client import Counter, Histogram
from stream_framework.metrics.base import Metrics

feed_reads = Counter('feed_reads', 'Feed read operations', ['feed'])
feed_writes = Counter('feed_writes', 'Feed write operations', ['feed'])
feed_deletes = Counter('feed_deletes', 'Feed delete operations', ['feed'])

activities_published = Counter('feed_activities_published', 'Published feed activities')
activities_removed = Counter('feed_activities_removed', 'Removed feed activities')

on_fanout = Counter('feed_fanout', 'Feed fanout operations', ['feed', 'operation'])

fanout_timer = Histogram('feed_fanout_timer', 'Time the fanout task', ['feed'])
feed_read_timer = Histogram('feed_read_timer', 'Time feed read operations', ['feed'])


class PrometheusFeedMetrics(Metrics):

    def fanout_timer(self, feed_class):
        return fanout_timer.labels(feed=feed_class.__name__).time()

    def feed_reads_timer(self, feed_class):
        return feed_read_timer.labels(feed=feed_class.__name__).time()

    def on_feed_read(self, feed_class, activities_count):
        feed_reads.labels(feed=feed_class.__name__).inc(activities_count)

    def on_feed_write(self, feed_class, activities_count):
        feed_writes.labels(feed=feed_class.__name__).inc(activities_count)

    def on_feed_remove(self, feed_class, activities_count):
        feed_deletes.labels(feed=feed_class.__name__).inc(activities_count)

    def on_fanout(self, feed_class, operation, activities_count=1):
        on_fanout.labels(
            feed=feed_class.__name__, operation=operation.__name__
        ).inc(activities_count)

    def on_activity_published(self):
        activities_published.inc()

    def on_activity_removed(self):
        activities_removed.inc()
