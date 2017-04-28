from django.conf import settings
from statsd.client import StatsClient

statsd = None


if statsd is None:
    statsd = StatsClient(
        host=getattr(settings, 'STATSD_HOST', '127.0.0.1'),
        port=getattr(settings, 'STATSD_PORT', 9125),
        prefix=getattr(settings, 'STATSD_PREFIX', 'lego')
    )
