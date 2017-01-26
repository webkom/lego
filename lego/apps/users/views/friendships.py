from rest_framework import viewsets

from lego.apps.users.models import Friendship
from lego.apps.users.serializers import FriendshipSerializer


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    ordering = 'id'
