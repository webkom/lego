from lego.apps.reactions.models import Reaction, ReactionType
from lego.apps.reactions.permissions import ReactionPermission
from lego.apps.reactions.serializers import ReactionSerializer, ReactionTypeSerializer
from rest_framework import mixins, viewsets

class ReactionTypeViewSet(viewsets.ModelViewSet):
    queryset = ReactionType.objects.all()
    serializer_class = ReactionTypeSerializer

class ReactionViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Reaction.objects.all()
    permission_classes = (ReactionPermission,)
    serializer_class = ReactionSerializer
