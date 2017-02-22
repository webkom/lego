from rest_framework import viewsets

from lego.apps.permissions.permissions import AbakusPermission
from lego.apps.trophies.models import Trophy
from lego.apps.trophies.serializers import TrophySerializer


class TrophyViewSet(viewsets.ModelViewSet):
    queryset = Trophy.objects.all()
    permission_classes = [AbakusPermission]
    serializer_class = TrophySerializer
    ordering = 'id'

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('users')

        return self.queryset
