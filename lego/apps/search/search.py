from lego.apps.stats.utils import track

from . import backend
from .permissions import has_permission


def autocomplete(query, types, user):
    result = backend.current_backend.autocomplete(query, types)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['id'], user)

    result = list(filter(permission_check, result))

    track(
        user,
        'search.autocomplete',
        properties={
            'query': query,
            'result_count': len(result)
        },
    )

    return result


def search(query, types, filters, user):
    result = backend.current_backend.search(query, types, filters)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['id'], user)

    result = list(filter(permission_check, result))

    track(
        user,
        'search.search',
        properties={
            'query': query,
            'result_count': len(result)
        },
    )

    return result
