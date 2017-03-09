from lego.apps.meetings.models import Meeting
from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.permissions.permissions import AbakusPermission


class MeetingPermissionIndex(PermissionIndex):

    queryset = Meeting.objects.all()

    list = ['/sudo/admin/meetings/list/']
    retrieve = ['/sudo/admin/meetings/retrieve/']
    create = ['/sudo/admin/meetings/create/']
    update = ['/sudo/admin/meetings/update/']
    partial_update = ['/sudo/admin/meetings/update/']
    destroy = ['/sudo/admin/meetings/destroy/']


register(MeetingPermissionIndex)


class MeetingPermissions(AbakusPermission):

    check_object_permission = True

    def has_object_permission(self, request, view, meeting):
        if super().has_object_permission(request, view, meeting):
            return True
        if view.action == 'destroy':
            return meeting.created_by == request.user
        return meeting.can_edit(request.user)


class MeetingInvitationPermissions(AbakusPermission):

    def has_permission(self, request, view):
        meeting = Meeting.objects.get(id=view.kwargs['meeting_pk'])
        return meeting.can_edit(request.user)

    def has_object_permission(self, request, view, invitation):
        if super(MeetingInvitationPermissions, self)\
                    .has_object_permission(request, view, invitation):
            return True
        user = request.user
        meeting = invitation.meeting
        if view.action == 'destroy':
            return meeting.created_by == user
        return meeting.created_by == user or invitation.user == user
