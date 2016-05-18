from lego.search.es import backend as elasticsearch_backend

from .permissions import has_permission


def autocomplete(query, user):
    result = elasticsearch_backend.autocomplete(query)
    if has_permission(result['content_type'], result['object_id'], user):
        return result
    return None


def search(query, user):
    result = elasticsearch_backend.search(query)

    def filter_func(hit):
        return has_permission(hit['content_type'], hit['object_id'], user)

    return filter(filter_func, result)
