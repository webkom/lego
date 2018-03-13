Stats
=====

Lego has two types of interfaces to send analytics to external systems:

* prometheus - Send application specific information for alerting on app performance and so on.
* analytics - Send mostly BI events to our analytics backend.
* Elastic APM - App metrics and tracing functionality.

Prometheus
----------

We use prometheus to track application performance.

::

    from prometheus_client import Summary, Counter

    SEARCH_INDEX_COUNTER = Counter('search_index', 'Search backend index')
    SEARCH_INDEX_COUNTER.inc()

    HAS_PERMISSIONS_SUMMARY = Summary('permissions_has_perm', 'Permissions has perm')

    @HAS_PERMISSIONS_SUMMARY.time()
    def has_permission(self, request, view):
        do work...

Analytics
---------

::

    from lego.apps.stats.analytics_client import track

    track(
        user,
        'event.view',
        properties={'event': event.id},
    )

We also has a wrapper around the logger framework and the analytics exporter. This is a good way
to track "BI" events and at the same time improve the logging.

::

    from lego.apps.stats.utils import track

    track(
        user,
        'event.view',
        properties={'event': event.id},
    )

Elastic APM
-----------

Automatically collected by the elastic-apm package.
