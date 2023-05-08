from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.users.filters import PenaltyGroupFilterSet
from lego.apps.users.models import PenaltyGroup
from lego.apps.users.serializers.penalties import PenaltyGroupSerializer


class PenaltyGroupViewSet(
    AllowedPermissionsMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = PenaltyGroup.objects.all()
    serializer_class = PenaltyGroupSerializer
    filterset_class = PenaltyGroupFilterSet
