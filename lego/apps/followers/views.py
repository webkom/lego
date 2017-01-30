from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from lego.apps.followers.models import FollowEvent, FollowUser
from lego.apps.followers.permissions import FollowerPermission
from lego.apps.followers.serializers import FollowEventSerializer, FollowUserSerializer

from .filters import FollowEventFilterSet, FollowUserFilterSet


class FollowerBaseViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          mixins.DestroyModelMixin, viewsets.GenericViewSet):

    filter_backends = [DjangoFilterBackend]
    permission_classes = [FollowerPermission]


class FollowUserViewSet(FollowerBaseViewSet):
    serializer_class = FollowUserSerializer
    queryset = FollowUser.objects.all().select_related('follower')
    filter_class = FollowUserFilterSet


class FollowEventViewSet(FollowerBaseViewSet):
    serializer_class = FollowEventSerializer
    queryset = FollowEvent.objects.all().select_related('follower')
    filter_class = FollowEventFilterSet
