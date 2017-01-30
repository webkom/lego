from django_filters.filterset import FilterSet

from .models import FollowEvent, FollowUser


class FollowUserFilterSet(FilterSet):

    class Meta:
        model = FollowUser
        fields = ('target', 'follower')


class FollowEventFilterSet(FilterSet):

    class Meta:
        model = FollowEvent
        fields = ('target', 'follower')
