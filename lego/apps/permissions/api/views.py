from rest_framework.response import Response
from rest_framework.routers import SimpleRouter

from lego.apps.permissions.actions import action_to_permission
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.stats.statsd_client import statsd

permission_cache = {}


def permission_handler(view, model):
    handler = getattr(
        view, 'permission_handler', None
    )
    if not handler:
        handler = get_permission_handler(model)

    return handler


@statsd.timer('permissions.action_grant')
def get_viewset_permissions(viewset, model, user, obj, queryset):
    """
    Return a list of actions a user can perform on a viewset. We use the SimpleRouter to extract
    routes from viewsets. Possible actions per viewset is cached in memory. The next thing we do
    is to check permissions on all actions using the AbakusPermission backend.
    """

    router = SimpleRouter()
    viewset_cls = viewset.__class__

    def get_permissions(viewset_cls):
        routes = router.get_routes(viewset_cls)
        actions = []
        for route in routes:
            actions += route.mapping.values()
        return [action_to_permission(action) for action in actions]

    permissions = permission_cache[viewset_cls] if viewset_cls in permission_cache else \
        permission_cache.setdefault(viewset_cls, get_permissions(viewset_cls))

    handler = permission_handler(viewset, model)

    return handler.permissions_grant(permissions, user, obj, queryset)


def wrap_results(response):
    """
    Turns response.data into a dict,
    in case the inheritee isn't using pagination.
    """
    if isinstance(response.data, list):
        return {
            'results': response.data
        }

    return response.data


class AllowedPermissionsMixin:
    """
    Append a `permission` value on list and retrieve methods. This makes it possible for a
    frontend to decide which actions a user can perform.
    """
    def __init__(self, *args, **kwargs):
        if hasattr(super(), 'list'):
            self.list = self._list
        if hasattr(super(), 'retrieve'):
            self.retrieve = self._retrieve

        super().__init__(*args, **kwargs)

    def _list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data = wrap_results(response)
        response.data['action_grant'] = get_viewset_permissions(
            self, self.get_queryset().model, request.user, None, self.get_queryset()
        )
        return response

    def _retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        response = Response(serializer.data)
        response.data = wrap_results(response)
        response.data['action_grant'] = get_viewset_permissions(
            self, self.get_queryset().model, request.user, obj, self.get_queryset()
        )
        return response
