from lego.apps.permissions.constants import CREATE, EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from django.apps import apps


class LendableObjectPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendableobjects/{perm}/"


class LendingRequestPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/lendingrequests/{perm}/"

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        
        if perm is LIST or perm is VIEW or perm is CREATE:
            return True
        
        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )