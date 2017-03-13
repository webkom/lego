from structlog import get_logger

from lego.apps.events.models import Registration
from lego.apps.permissions.permissions import AbakusPermission

log = get_logger()


class PoolPermissions(AbakusPermission):
    pass


class RegistrationPermissions(AbakusPermission):
    """
    This allows users to update and destroy the registration object.
    Update is used to set new feedback and destroy is used to unregister.

    Note: Users are given keyword permission to create (register), however they can only register
    to events that are not filtered away meaning we can still create events that are hidden
    e.g. "Helgesamling" that regular users cant register to.
    """
    allowed_individual = ['retrieve', 'update', 'partial_update', 'destroy']

    def is_self(self, request, view, obj=None):
        if view.action in self.allowed_individual:
            registration_id = view.kwargs.get('pk', None)
            reg = Registration.objects.get(pk=registration_id)
            if obj and obj.user == request.user:
                return True
            if reg and request.user.id == reg.user_id:
                return True

    def has_permission(self, request, view):
        if self.is_self(request, view):
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if self.is_self(request, view, obj):
            return True
        return super().has_object_permission(request, view, obj)


class AdminRegistrationPermissions(AbakusPermission):
    pass
