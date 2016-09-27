from lego.apps.permissions.permissions import AbakusPermission


class MeetingPermissions(AbakusPermission):
    def has_object_permission(self, request, view, meeting):
        user = request.user
        if user.id in meeting.invited_user_ids().all():
            return True
        if meeting.only_for_invited:
            return False
        return super().has_object_permission(request, view, meeting)
