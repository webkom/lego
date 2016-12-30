from rest_framework import mixins, viewsets

from lego.apps.permissions.views import AllowedPermissionsMixin
from lego.apps.reactions.models import Reaction, ReactionType
from lego.apps.reactions.permissions import ReactionPermission
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
    permission_classes = (ReactionPermission,)
    serializer_class = ReactionSerializer
