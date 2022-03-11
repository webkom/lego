from django_filters import ModelChoiceFilter
from django_filters.filterset import FilterSet

from lego.apps.events.models import Event

from .models import FollowCompany, FollowUser


class FollowUserFilterSet(FilterSet):
    class Meta:
        model = FollowUser
        fields = ("target", "follower")


class FollowEventFilterSet(FilterSet):
    target = ModelChoiceFilter(queryset=Event.objects.all())

    class Meta:
        fields = "target"


class FollowCompanyFilterSet(FilterSet):
    class Meta:
        model = FollowCompany
        fields = ("target", "follower")
