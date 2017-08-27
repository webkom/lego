Stats
=====

Lego has two types of interfaces to send analytics to external systems:

* statsd - Send application specific information for alerting on app performance and so on.
* analytics - Send mostly BI events to our analytics backend.

STATSD
------

::

    from lego.apps.stats.statsd_client import statsd

    statsd.incr('search.search_index', 1)

    @statsd.timer('permissions.has_permission')
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
