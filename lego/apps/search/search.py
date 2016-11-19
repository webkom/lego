from lego.apps.search.backends.elasticsearch import backend as elasticsearch_backend

from .permissions import has_permission


def autocomplete(query, types, user):
    result = elasticsearch_backend.autocomplete(query, types)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['object_id'], user)

    return filter(permission_check, result)


def search(query, types, user):
    result = elasticsearch_backend.search(query, types)

    def permission_check(hit):
        return has_permission(hit['content_type'], hit['object_id'], user)

    return filter(permission_check, result)
