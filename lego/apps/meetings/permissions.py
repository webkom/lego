from lego.apps.meetings.models import Meeting
from lego.apps.permissions.permissions import AbakusPermission


class MeetingPermissions(AbakusPermission):

    def has_object_permission(self, request, view, meeting):
        if not super().has_object_permission(request, view, meeting):
            return False
        if view.action == 'destroy':
            return meeting.created_by == request.user
        return meeting.can_edit(request.user)


class MeetingInvitationPermissions(AbakusPermission):

    def has_permission(self, request, view):
        meeting = Meeting.objects.get(id=view.kwargs['meeting_pk'])
        return meeting.can_edit(request.user)

    def has_object_permission(self, request, view, invitation):
        if not super(MeetingInvitationPermissions, self)\
                    .has_object_permission(request, view, invitation):
            return False
        user = request.user
        meeting = invitation.meeting
        if view.action == 'destroy':
            return meeting.created_by == user
        return meeting.can_edit(user)
