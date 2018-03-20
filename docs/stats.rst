Stats
=====

Lego has one interface for sending analytics to external systems:

* analytics - Send mostly BI events to our analytics backend.

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
