from rest_framework.permissions import IsAuthenticated


class FollowerPermission(IsAuthenticated):

    def has_permission(self, request, view):
        if view.action == 'destroy':
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return request.user == obj.follower
