from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Model

from . import backend
from .permissions import has_permission

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

    from lego.apps.users.models import User


def autocomplete(
    query: str, types: list[str], user: User | AnonymousUser
) -> list[dict]:
    results = backend.current_backend.autocomplete(query, types)

    def permission_check(hit: Model) -> bool:
        instance = backend.current_backend.get_django_object(hit)
        if instance:
            return has_permission(instance, user)
        else:
            return False

    results = list(filter(permission_check, results))

    return backend.current_backend.serialize(results)


def search(
    query: str, types: list[str], filters: dict, user: User | AnonymousUser
) -> list[dict]:
    results = backend.current_backend.search(query, types, filters)

    def permission_check(hit: Model) -> bool:
        instance = backend.current_backend.get_django_object(hit)
        if instance:
            return has_permission(instance, user)
        else:
            return False

    results = list(filter(permission_check, results))

    return backend.current_backend.serialize(results, search_type="search")
