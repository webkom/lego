from lego.apps.stats.statsd_client import statsd

from . import backend
from .permissions import has_permission


@statsd.timer('search.autocomplete_query')
def autocomplete(query, types, user):
    result = backend.current_backend.autocomplete(query, types)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['id'], user)

    return filter(permission_check, result)


@statsd.timer('search.search_query')
def search(query, types, filters, user):
    result = backend.current_backend.search(query, types, filters)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['id'], user)

    return filter(permission_check, result)
