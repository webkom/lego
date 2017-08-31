from rest_framework import mixins, viewsets

from lego.apps.followers.models import FollowCompany, FollowEvent, FollowUser
from lego.apps.followers.serializers import (FollowCompanySerializer, FollowEventSerializer,
                                             FollowUserSerializer)

from .filters import FollowCompanyFilterSet, FollowEventFilterSet, FollowUserFilterSet


class FollowerBaseViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class FollowUserViewSet(FollowerBaseViewSet):
    serializer_class = FollowUserSerializer
    queryset = FollowUser.objects.all().select_related('follower')
    filter_class = FollowUserFilterSet


class FollowEventViewSet(FollowerBaseViewSet):
    serializer_class = FollowEventSerializer
    queryset = FollowEvent.objects.all().select_related('follower')
    filter_class = FollowEventFilterSet


class FollowCompanyViewSet(FollowerBaseViewSet):
    serializer_class = FollowCompanySerializer
    queryset = FollowCompany.objects.all().select_related('follower')
    filter_class = FollowCompanyFilterSet
