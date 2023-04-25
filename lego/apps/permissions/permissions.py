from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterable, Sequence, Type, TypeVar

from django.db.models import Q, QuerySet

from lego.apps.permissions.constants import CREATE, LIST, VIEW
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel

if TYPE_CHECKING:
    from lego.apps.users.models import User


def _check_intersection(first, second) -> bool:
    return len(set(first).intersection(set(second))) > 0


T = TypeVar("T", bound=BasisModel)


class PermissionHandler(Generic[T]):
    """
    The permission handler defines how permissions should be handled on a model

    Required functions and things we need to answer

    * Different actions a user can perform on a queryset (action_grant)
    * Different actions a user can perform on a object (action_grant)
    * Filter querysets based on permissions
    * Check permissions on a per object level
    * Support custom permission actions

    Usage:
    class Test(models.Model):

        class Meta:
            permissions = PermissionHandler()
    """

    default_keyword_permission = "/sudo/admin/{model_name}s/{perm}/"
    default_require_auth = True

    permission_map = {}
    authentication_map = {}
    safe_methods = [VIEW, LIST]

    # Sometimes we need to call the has_object_permission if the model isn't based on the
    # ObjectPermissionsModel
    force_object_permission_check = False
    # We may also be able to skip the has_object_permission it the model is based on the
    # ObjectPermissionsModel
    skip_object_permission = False
    # Sometimes we need use the filter function to display permitted elements.
    force_queryset_filtering = False

    perms_without_object = [CREATE]

    def permissions_grant(
        self,
        permissions: Sequence[str],
        user: User,
        obj: T | None = None,
        queryset: QuerySet[T] | None = None,
    ) -> list[str]:
        """
        Lookup possible permissions the user has access to.
        """
        permissions = list(set(permissions))

        filtered_permissions: Iterable[str] = []
        if obj is not None:
            filtered_permissions = filter(
                lambda perm: user.has_perm(perm, obj), permissions
            )
        elif queryset is not None:
            filtered_permissions = filter(
                lambda perm: user.has_perm(perm, queryset), permissions
            )

        return list(filtered_permissions)

    def has_object_level_permissions(
        self,
        user: User,
        perm: str,
        obj: T | None = None,
        queryset: QuerySet[T] | None = None,
    ) -> bool:
        """
        Check whether the queryset or object requires a permission check at object level.
        This function should only be used by the api permission backend.
        """

        if perm in self.perms_without_object:
            return False

        if obj is None and queryset is None:
            raise ValueError(
                "You have to at least provide one parameter, obj or queryset."
            )
        elif self.force_object_permission_check and self.skip_object_permission:
            raise ValueError(
                "You cannot force and skip the permission checks at the same time!"
            )

        require_auth = self.require_auth(perm, obj, queryset)
        authenticated = self.is_authenticated(user)

        if not require_auth:
            return True
        elif require_auth and not authenticated:
            return False

        if self.force_object_permission_check and perm != "list":
            return True
        elif self.skip_object_permission:
            return False

        if obj is not None:
            if isinstance(obj, ObjectPermissionsModel):
                return True
            if obj.created_by == user:
                return True

        if queryset is not None and issubclass(queryset.model, ObjectPermissionsModel):
            return True

        return self.force_queryset_filtering

    def has_perm(
        self,
        user: User,
        perm: str,
        obj: T | None = None,
        queryset: QuerySet[T] | None = None,
        check_keyword_permissions=True,
        **kwargs,
    ) -> bool:
        """
        Check permission on a object.
        """
        if obj is None and queryset is None:
            raise ValueError(
                "You have to at least provide one parameter, obj or queryset."
            )
        elif self.force_object_permission_check and self.skip_object_permission:
            raise ValueError(
                "You cannot force and skip the permission checks at the same time!"
            )

        require_auth = self.require_auth(perm, obj)
        authenticated = self.is_authenticated(user)

        if require_auth and not authenticated:
            return False
        elif not require_auth and perm in self.safe_methods:
            return True
        if not authenticated:
            return False

        if obj is not None:
            model = obj.__class__
        else:
            model = queryset.model
        if model is None:
            raise ValueError("The model is null, cannot continue.")

        if check_keyword_permissions:
            required_keyword_permissions = self.required_keyword_permissions(
                model, perm
            )
            has_perms = user.has_perms(required_keyword_permissions)
            if has_perms:
                return True

        if obj:
            created_by = self.created_by(user, obj)
            if created_by:
                return True

            if isinstance(obj, ObjectPermissionsModel):
                return self.has_object_permissions(user, perm, obj)

        return False

    def filter_queryset(
        self, user: User, queryset: QuerySet[T], **kwargs
    ) -> QuerySet[T]:
        """
        Filter queryset based on object-level permissions.
        We currently only supports queryset filtering on ObjectPermissionsModels.
        Don't use this function if you know that the user has list permissions.
        """
        if issubclass(queryset.model, ObjectPermissionsModel):
            # Unauthenticated users can only see objects with no auth required.
            if not user.is_authenticated:
                return queryset.filter(require_auth=False)

            # User is authenticated, display objects created by user or object with group rights.
            groups = [abakus_group.pk for abakus_group in user.all_groups]
            return queryset.filter(
                Q(can_edit_users__in=[user.pk])
                | Q(can_edit_groups__in=groups)
                | Q(can_view_groups__in=groups)
                | Q(created_by=user)
                | Q(require_auth=False)
            ).distinct()

        return queryset

    def require_auth(
        self, perm: str, obj: T | None = None, queryset: QuerySet[T] | None = None
    ) -> bool:
        require_auth = self.authentication_map.get(perm, self.default_require_auth)
        if not require_auth:
            return False

        if obj and isinstance(obj, ObjectPermissionsModel):
            return obj.require_auth

        if queryset is not None and hasattr(queryset.model, "require_auth"):
            return False

        return True

    def is_authenticated(self, user: User) -> bool:
        return user and user.is_authenticated

    def keyword_permission(self, model: Type[BasisModel], perm: str) -> str:
        """
        Create default permission string based on the model class, action and default_permission
        format. This is used when no permission is provided for a action in the permission_map.
        """
        kwargs = {
            "app_label": model._meta.app_label,
            "model_name": model._meta.model_name,
            "perm": perm,
        }
        return self.default_keyword_permission.format(**kwargs)

    def required_keyword_permissions(
        self, model: Type[BasisModel], perm: str
    ) -> list[str]:
        """
        Get required keyword permissions based on the action and model class.
        Override the permission_map to create custom permissions, the default_keyword_permission
        function is used otherwise.
        """

        return self.permission_map.get(perm, [self.keyword_permission(model, perm)])

    def created_by(self, user: User, obj: T) -> bool:
        created_by = getattr(obj, "created_by_id", None)
        return created_by == user.id

    def has_object_permissions(self, user: User, perm: str, obj: T) -> bool:
        if perm in self.safe_methods:
            # Check can_view
            if _check_intersection(
                user.all_groups, obj.can_view_groups.all() | obj.can_edit_groups.all()
            ):
                return True
            elif user in obj.can_edit_users.all():
                return True
            return False
        else:
            # Check can_edit
            if _check_intersection(user.all_groups, obj.can_edit_groups.all()):
                return True
            elif user in obj.can_edit_users.all():
                return True
            return False
