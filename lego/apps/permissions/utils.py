from rest_framework.routers import SimpleRouter
from structlog import get_logger

from .permissions import AbakusPermission

log = get_logger()


# The routes in a viewset is not changing. This makes it possible to store actions in memory.
action_cache = {}


def get_viewset_permissions(viewset, model, instance, user):
    """
    Return a list of actions a user can perform on a viewset. We use the SimpleRouter to extract
    routes from viewsets. Possible actions per viewset is cached in memory. The next thing we do
    is to check permissions on all actions using the AbakusPermission backend.
    """

    router = SimpleRouter()
    viewset_cls = viewset.__class__

    def get_actions(viewset_cls):
        log.debug('action_lookup', viewset=repr(viewset_cls))
        routes = router.get_routes(viewset_cls)
        actions = []
        for route in routes:
            actions += route.mapping.values()
        return actions

    actions = action_cache[viewset_cls] if viewset_cls in action_cache else \
        action_cache.setdefault(viewset_cls, get_actions(viewset_cls))

    abakus_backends = [
        permission for permission in viewset.get_permissions()
        if isinstance(permission, AbakusPermission)
    ]
    if len(abakus_backends) != 1:
        raise ValueError('Only one single AbakusPermission class is supported')
    backend = abakus_backends[0]

    if instance:
        def filter_function(action):
            return backend._has_object_permission(
                action, instance, user, action in backend.safe_actions
            )
    else:
        def filter_function(action):
            return backend._has_permission(action, model, user)

    return filter(filter_function, actions)
