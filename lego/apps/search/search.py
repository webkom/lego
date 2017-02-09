from prometheus_client import Summary

from . import backend
from .permissions import has_permission

autocomplete_timer = Summary('search_autocomplete', 'Track autocomplete requests')
search_timer = Summary('search_query', 'Track search query requests')


@autocomplete_timer.time()
def autocomplete(query, types, user):
    result = backend.current_backend.autocomplete(query, types)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['id'], user)

    return filter(permission_check, result)


@search_timer.time()
def search(query, types, filters, user):
    result = backend.current_backend.search(query, types, filters)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['id'], user)

    return filter(permission_check, result)
