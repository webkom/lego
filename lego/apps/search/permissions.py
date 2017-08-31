from django.core.exceptions import ObjectDoesNotExist

from lego.apps.permissions.constants import VIEW
from lego.utils.content_types import string_to_model_cls


def has_permission(content_type, pk, user):
    """
    Check permissions on a given content_type and pk.
    """
    model = string_to_model_cls(content_type)

    try:
        instance = model.objects.get(pk=pk)
        return user.has_perm(VIEW, instance)
    except ObjectDoesNotExist:
        pass

    return False
