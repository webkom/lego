from .utils import get_viewset_permissions


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
    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data = wrap_results(response)
        response.data['permissions'] = get_viewset_permissions(
            self, self.get_queryset().model, None, request.user
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, args, kwargs)
        response.data = wrap_results(response)
        response.data['permissions'] = get_viewset_permissions(
            self, self.get_queryset().model, self.get_object(), request.user
        )
        return response
