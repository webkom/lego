from lego.apps.permissions.permissions import AbakusPermission


class MeetingPermissions(AbakusPermission):
    def has_object_permission(self, request, view, meeting):
        user = request.user
        if user in meeting.invited_users():
            return True
        return super().has_object_permission(request, view, meeting)
