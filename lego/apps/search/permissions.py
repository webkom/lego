from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Model

from lego.apps.permissions.constants import VIEW

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

    from lego.apps.users.models import User


def has_permission(instance: Model, user: User | AnonymousUser) -> bool:
    # The permission mixin annotates `obj` too narrowly, hence the ignore.
    return bool(user.has_perm(VIEW, instance))  # type: ignore[misc, arg-type]
