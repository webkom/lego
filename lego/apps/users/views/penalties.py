
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from lego.apps.users.models import Penalty
from lego.apps.users.permissions import PenaltyPermissions
from lego.apps.users.serializers import PenaltySerializer


class PenaltyViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer
    permission_class = (PenaltyPermissions, )
