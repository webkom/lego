from rest_framework import permissions
from .models import ICalToken


class ICalTokenPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        raw_token = request.GET.get('token')

        if not raw_token:
            return False

        return ICalToken.objects.filter(token=raw_token).exists()

