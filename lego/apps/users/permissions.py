from lego.apps.permissions.api.permissions import LegoPermissions
from lego.apps.permissions.constants import CREATE, DELETE, EDIT, LIST, VIEW
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.users import constants

EDIT_ROLES = (constants.LEADER, constants.CO_LEADER)


class UserPermissionHandler(PermissionHandler):
    permission_map = {VIEW: []}  # type: ignore

    allowed_individual = [VIEW, EDIT]
    force_object_permission_check = True

    def is_self(self, perm, user, obj):
        if user.is_authenticated and obj is not None:
            return perm in self.allowed_individual and obj == user
        return False

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        is_self = self.is_self(perm, user, obj)
        if is_self:
            return True

        return super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )


class AbakusGroupPermissionHandler(PermissionHandler):
    permission_map = {LIST: [], VIEW: []}
    authentication_map = {LIST: False, VIEW: False}

    force_object_permission_check = True
    default_keyword_permission = "/sudo/admin/groups/{perm}/"

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        if perm == DELETE:
            return False

        has_perm = super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )

        if has_perm:
            return True

        if user.is_authenticated and obj is not None:
            return obj.memberships.filter(user=user, role__in=EDIT_ROLES).exists()

        return False


class PreventPermissionElevation(LegoPermissions):
    def has_permission(self, request, view):
        if request.method in ["CREATE", "PUT", "PATCH"]:
            user = request.user
            requested_permissions = request.data.get("permissions", [])

            if not user.has_perms(requested_permissions):
                return False

        return super().has_permission(request, view)


class MembershipPermissionHandler(PermissionHandler):
    force_object_permission_check = True
    default_keyword_permission = "/sudo/admin/groups/{perm}/"

    def has_perm(
        self,
        user,
        perm,
        obj=None,
        queryset=None,
        check_keyword_permissions=True,
        **kwargs
    ):
        has_perm = super().has_perm(
            user, perm, obj, queryset, check_keyword_permissions, **kwargs
        )

        if has_perm:
            return True

        if not user.is_authenticated:
            # Don't allow any unauthorized users see memberships
            return False

        if obj is not None:
            if perm == EDIT and obj.abakus_group.type in constants.OPEN_GROUPS:
                # Retrieve parent group
                view = kwargs.get("view", None)
                if view is None:
                    return False
                abakus_group_pk = view.kwargs["group_pk"]
                from lego.apps.users.models import AbakusGroup

                abakus_group = AbakusGroup.objects.get(id=abakus_group_pk)

                request = kwargs.get("request", None)
                if not request:
                    return False
                data = request.data
                role = data.get("role")
                if (
                    role != constants.MEMBER
                    and not abakus_group.memberships.filter(
                        user=user, role__in=EDIT_ROLES
                    ).exists()
                ):
                    return False
            return obj.abakus_group.type in constants.OPEN_GROUPS and obj.user == user

        # Retrieve parent group
        view = kwargs.get("view", None)
        if view is None:
            return False
        abakus_group_pk = view.kwargs["group_pk"]
        from lego.apps.users.models import AbakusGroup

        abakus_group = AbakusGroup.objects.get(id=abakus_group_pk)

        if abakus_group.type in constants.PUBLIC_GROUPS:
            if perm == LIST:
                return True

        if abakus_group.type in constants.OPEN_GROUPS:
            if perm == LIST:
                return True
            elif perm == DELETE:
                # Leaders should be able to remove memberships.
                return abakus_group.memberships.filter(
                    user=user, role__in=EDIT_ROLES
                ).exists()
            elif perm == CREATE:
                # Creating a memberships in open groups as yourself is allowed.
                request = kwargs.get("request", None)
                if not request:
                    return False
                data = request.data
                role = data.get("role")
                if (
                    role != constants.MEMBER
                    and not abakus_group.memberships.filter(
                        user=user, role__in=EDIT_ROLES
                    ).exists()
                ):
                    return False
                return data.get("user") == user.id

        return False
