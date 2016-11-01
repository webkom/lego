from rest_framework import viewsets

from lego.apps.users.models import Penalty
from lego.apps.users.serializers import PenaltySerializer


class PenaltyViewSet(viewsets.ModelViewSet):
    queryset = Penalty.objects.all()
    serializer_class = PenaltySerializer
