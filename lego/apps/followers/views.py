from rest_framework import mixins, viewsets

from lego.apps.followers.models import FollowCompany, FollowEvent, FollowUser
from lego.apps.followers.serializers import (
    FollowCompanySerializer,
    FollowEventSerializer,
    FollowUserSerializer,
)
from lego.apps.permissions.utils import get_permission_handler

from .filters import FollowCompanyFilterSet, FollowEventFilterSet, FollowUserFilterSet


class FollowerBaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        queryset = super().get_queryset()
        permission_handler = get_permission_handler(queryset.model)
        return permission_handler.filter_queryset(self.request.user, queryset)


class FollowUserViewSet(FollowerBaseViewSet):
    serializer_class = FollowUserSerializer
    queryset = FollowUser.objects.all().select_related("follower")
    filter_class = FollowUserFilterSet


class FollowEventViewSet(FollowerBaseViewSet):
    serializer_class = FollowEventSerializer
    queryset = FollowEvent.objects.all().select_related("follower")
    filter_class = FollowEventFilterSet


class FollowCompanyViewSet(FollowerBaseViewSet):
    serializer_class = FollowCompanySerializer
    queryset = FollowCompany.objects.all().select_related("follower")
    filter_class = FollowCompanyFilterSet
