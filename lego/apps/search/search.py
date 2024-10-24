from . import backend
from .permissions import has_permission


def autocomplete(query, types, user):
    results = backend.current_backend.autocomplete(query, types)

    def permission_check(hit):
        instance = backend.current_backend.get_django_object(hit)
        if instance:
            return has_permission(instance, user)
        else:
            return False

    results = list(filter(permission_check, results))

    return backend.current_backend.serialize(results)


def search(query, types, filters, user):
    results = backend.current_backend.search(query, types, filters)

    def permission_check(hit):
        instance = backend.current_backend.get_django_object(hit)
        if instance:
            return has_permission(instance, user)
        else:
            return False

    results = list(filter(permission_check, results))

    return backend.current_backend.serialize(results, search_type="search")
