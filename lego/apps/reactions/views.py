from rest_framework import mixins, viewsets

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.reactions.models import Reaction
from lego.apps.reactions.serializers import ReactionSerializer


class ReactionViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
