from rest_framework import permissions

from .models import ICalToken


class ICalTokenPermission(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        super().has_permission(request, view)
        if not request.user.is_anonymous():
            request.token_user = request.user
            return True

        raw_token = request.GET.get('token')
        if not raw_token:
            return False

        token = ICalToken.objects.filter(token=raw_token)
        if not token.exists():
            return False
        request.token_user = token[0].user
        return True
