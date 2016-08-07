Feeds
=====

Lego uses the `stream-framework <https://github.com/tschellenbach/Stream-Framework>`_ for feed
generation. We are currently utilizing the Redis backend, but it is possible to change to
Cassandra later.

Every element in a feed is based on one or more activities. Every feed uses a manager to handle
activity creation and deletion.

Lego uses a custom activity class called FeedActivity. This class makes it possible to relate
django orm objects to a activity. This custom class translates a object to a identifier string
(app_name.model_name-object_id).

Installed feeds
---------------

* Notifications (Support for seen and read values, aggregated)
