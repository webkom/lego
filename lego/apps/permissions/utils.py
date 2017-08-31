from lego.apps.permissions.permissions import PermissionHandler


default_permission_handler = PermissionHandler()


def get_permission_handler(model):
    """
    Try to get the permission handler used by the model or use the default handler.
    """
    permission_handler = getattr(model._meta, 'permission_handler', default_permission_handler)
    return permission_handler
