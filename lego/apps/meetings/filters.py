from django.db.models import Q
from rest_framework import filters


def filter_queryset(user, queryset):
    return queryset.filter(
        Q(_invited_users=user) | Q(created_by=user)
    ).distinct()


class MeetingFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user
        return filter_queryset(user, queryset)
