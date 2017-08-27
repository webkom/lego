Site Search
===========

Elasticsearch are used to search and aggregate results when users queries the content stored in
Lego. We watch model changes using django signals and indexes changes in async celery tasks.

The application exposes two endpoints used to search content:

* ``/api/v1/search-search/`` that returns the result of an actual search query used to populate a results page.
* ``/api/v1/search-autocomplete/`` that returns a list of possible items to fill in a dropdown.

You have to implement a ``SearchIndex`` to make a model searchable. Please use a new
SearchSerializer when implementing an index, this makes things much easier to debug.


SearchIndex
-----------
.. automodule:: lego.apps.search.index
    :members:
    :show-inheritance:
