Stats
=====

Lego has two types of interfaces to send analytics to external systems:

* statsd - Send application specific information for alerting on app performance and so on.
* analytics - Send mostly BI events to our analytics backend.

STATSD
------

We use statsd to track application performance.

::

    from lego.apps.stats.statsd_client import statsd

    statsd.incr('search.search_index', 1)

    @statsd.timer('permissions.has_permission')
    def has_permission(self, request, view):
        do work...

The application track the following events:

+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.feed.attr_cache_context                 | Tracks the amount of time used to attach metadata to a feed request.       |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.activities.published                    | Published feed activities.                                                 |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.activities.removed                      | Removed feed activities.                                                   |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.<FEED_CLASS>.fanout_latency             |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.<FEED_CLASS>.read_latency               |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.<FEED_CLASS>.reads                      |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.<FEED_CLASS>.writes                     |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.<FEED_CLASS>.deletes                    |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.<FEED_CLASS>.fanout.<ACTION>            |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.authentication.authenticate.<PROVIDER>  | Track usage of different auth providers.                                   |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.restricted_mail.process_message         | Track the time used to process a restricted email message.                 |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.permissions.has_perm                    |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.permissions.api_filter_queryset         |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.permissions.api_has_permission          |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.permissions.api_has_object_permission   |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.permissions.api_action_grant            |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.search.autocomplete_query               | Track the time it takes to do a autocomplete request.                      |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.search.search_query                     | Track the time it takes to do a search request.                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.search.search_index                     | Models added to the search index.                                          |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.search.search_remove                    | Models removed from the search index.                                      |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.instance.create.<APP>.<MODEL>           | Track instance creation.                                                   |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.instance.update.<APP>.<MODEL>           | Track instance updates.                                                    |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.instance.delete.<APP>.<MODEL>           | Track instance deletion.                                                   |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.task.send_email                         | Track time spent on sending emails.                                        |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.task.send_push                          | Track time spent used on sending push messages.                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.request.total.<METHOD>                  |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.response.total.<METHOD>                 |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.request.latency.<METHOD>                |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.response.latency.<METHOD>               |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.request.unknown_latency.<METHOD>        |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+
| <PREFIX>.response.unknown_latency.<METHOD>       |                                                                            |
+--------------------------------------------------+----------------------------------------------------------------------------+

We use the Prometheus statsd exporter to collect these metrics. The following config parses the
metrics and collects the tag:

*We use lego.production or lego.staging as statsd prefix.*

::

    *.*.feed.attr_cache_context
    name="feed_attr_cache"
    system="$1"
    environment="$2"

    *.*.activities.*
    name="feed_activity_actions"
    system="$1"
    environment="$2"
    action="$3"

    *.*.*.fanout_latency
    name="feed_fanout_latency"
    system="$1"
    environment="$2"
    feed="$3"

    *.*.*.read_latency
    name="feed_read_latency"
    system="$1"
    environment="$2"
    feed="$3"

    *.*.*.reads
    name="feed_reads"
    system="$1"
    environment="$2"
    feed="$3"

    *.*.*.writes
    name="feed_writes"
    system="$1"
    environment="$2"
    feed="$3"

     *.*.*.deletes
    name="feed_deletes"
    system="$1"
    environment="$2"
    feed="$3"

    *.*.*.fanout.*
    name="feed_fanout"
    system="$1"
    environment="$2"
    feed="$3"
    action="$4"

    *.*.authentication.authenticate.*
    name="authentication_authenticate"
    system="$1"
    environment="$2"
    provider="$3"

    *.*.restricted_mail.process_message
    name="restricted_mail_process_message"
    system="$1"
    environment="$2"

    *.*.permissions.has_perm
    name="permissions_has_perm"
    system="$1"
    environment="$2"

    *.*.permissions.api_filter_queryset
    name="permissions_api_filter_queryset"
    system="$1"
    environment="$2"

    *.*.permissions.api_has_permission
    name="permissions_api_has_permission"
    system="$1"
    environment="$2"

    *.*.permissions.api_has_object_permission
    name="permissions_api_has_object_permission"
    system="$1"
    environment="$2"

    *.*.permissions.api_action_grant
    name="permissions_api_action_grant"
    system="$1"
    environment="$2"

    *.*.search.autocomplete_query
    name="search_autocomplete_query"
    system="$1"
    environment="$2"

    *.*.search.search_query
    name="search_search_query"
    system="$1"
    environment="$2"

    *.*.search.search_index
    name="search_search_index"
    system="$1"
    environment="$2"

    *.*.search.search_remove
    name="search_search_remove"
    system="$1"
    environment="$2"

    *.*.instance.*.*.*
    name="instance_event"
    system="$1"
    environment="$2"
    action="$3"
    application="$4"
    model="$5"

    *.*.task.*
    name="task_timing"
    system="$1"
    environment="$2"
    task="$3"

    *.*.request.total.*
    name="request_total"
    system="$1"
    environment="$2"
    method="$3"

    *.*.response.total.*
    name="response_total"
    system="$1"
    environment="$2"
    method="$3"

    *.*.request.latency.*
    name="request_latency"
    system="$1"
    environment="$2"
    method="$3"

    *.*.response.latency.*
    name="response_latency"
    system="$1"
    environment="$2"
    method="$3"

    *.*.request.unknown_latency.*
    name="request_unknown_latency"
    system="$1"
    environment="$2"
    method="$3"

    *.*.response.unknown_latency.*
    name="response_unknown_latency"
    system="$1"
    environment="$2"
    method="$3"

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
