from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.content_types import string_to_model_cls


def has_permission(content_type, pk, user):
    """
    Check permissions on a given content_type and pk.
    Check the default permission string for the model and object.can_view if possible.

    This is a simplified permissions check that checks the required defaults. We don't care about
    custom permission implementations. Our permission system are tightly coupled with the
    request-response cycle and it's a non-trivial task to use that system to resolve search
    permissions.
    TODO: Rewrite permissions...
    """
    model = string_to_model_cls(content_type)

    # Check permission string
    permission_string = '/sudo/admin/{model_name}s/retrieve/'.format(
        model_name=model._meta.model_name
    )
    if user.has_perm(permission_string):
        return True

    # Check ObjectPermissionsModel
    if issubclass(model, ObjectPermissionsModel):
        instance = model.objects.get(pk=pk)
        if instance.can_view(user):
            return True

    return False
