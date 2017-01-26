from rest_framework import viewsets

from lego.apps.followers.models import Follower
from lego.apps.followers.serializers import FollowerSerializer


class FollowersViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
