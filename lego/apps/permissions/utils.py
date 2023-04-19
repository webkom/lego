from typing import TypeVar

from lego.apps.permissions.permissions import PermissionHandler

# isort:skip

default_permission_handler = PermissionHandler()


T = TypeVar("T")


def get_permission_handler(model: T) -> PermissionHandler[T]:
    """
    Try to get the permission handler used by the model or use the default handler.
    """
    permission_handler = getattr(
        model._meta, "permission_handler", default_permission_handler
    )
    return permission_handler
