from lego.apps.meetings.models import Meeting
from lego.apps.permissions.permissions import AbakusPermission


class MeetingPermissions(AbakusPermission):

    def has_object_permission(self, request, view, meeting):
        if view.action == 'destroy':
            return super().has_object_permission(request, view, meeting)
        user = request.user
        if user in meeting.invited_users.all():
            return True
        if meeting.only_for_invited:
            return False
        return super().has_object_permission(request, view, meeting)


class MeetingInvitationPermissions(AbakusPermission):
    permission_map = {'create': []}

    def has_permission(self, request, view):
        has_permission = super(MeetingInvitationPermissions, self).has_permission(request, view)
        if not has_permission:
            return False

        meeting = Meeting.objects.get(id=view.kwargs['meeting_pk'])
        if not meeting.can_edit(request.user):
            return False
        return True
