from rest_framework import mixins, viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.reactions.models import Reaction, ReactionType
from lego.apps.reactions.serializers import ReactionSerializer, ReactionTypeSerializer


class ReactionTypeViewSet(AllowedPermissionsMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = ReactionType.objects.all()
    serializer_class = ReactionTypeSerializer


class ReactionViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
