from django.db.models import Q

from lego.apps.permissions.constants import DELETE
from lego.apps.permissions.permissions import PermissionHandler
from lego.apps.permissions.utils import get_permission_handler


class MeetingPermissionHandler(PermissionHandler):

    force_object_permission_check = True

    def filter_queryset(self, user, queryset, **kwargs):
        if user.is_authenticated():
            return queryset.filter(
                Q(_invited_users=user) | Q(created_by=user)
            ).distinct()
        return queryset.none()

    def has_object_level_permissions(self, user, perm, obj=None, queryset=None):
        if not user.is_authenticated():
            return False
        return super().has_object_level_permissions(user, perm, obj, queryset)

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if not user.is_authenticated():
            return False

        has_perm = super().has_perm(user, perm, obj, queryset, check_keyword_permissions, **kwargs)

        if has_perm:
            return True

        if obj is not None:
            return perm != DELETE and obj.invited_users.filter(id=user.id).exists()

        return False


class MeetingInvitationPermissionHandler(PermissionHandler):

    default_keyword_permission = '/sudo/admin/meetings/{perm}/'
    force_object_permission_check = True

    def has_perm(
            self, user, perm, obj=None, queryset=None, check_keyword_permissions=True, **kwargs
    ):
        if not user.is_authenticated():
            return False

        from lego.apps.meetings.models import Meeting

        if obj is not None:
            meeting = obj.meeting
        else:
            view = kwargs.get('view', None)
            if view is None:
                return False
            # This is a nested view and it is possible to retrieve the meeting.
            meeting_pk = view.kwargs['meeting_pk']
            meeting = Meeting.objects.get(id=meeting_pk)

        meeting_permission_handler = get_permission_handler(Meeting)
        has_perm = meeting_permission_handler.has_perm(
            user, perm, obj=meeting, queryset=Meeting.objects.none()
        )

        if has_perm:
            if perm in self.safe_methods:
                return True
            elif obj is not None:
                return obj.user == user

        return False
