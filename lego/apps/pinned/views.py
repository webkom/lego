from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.pinned.models import Pinned
from lego.apps.pinned.serializers import CreatePinnedSerializer, ListPinnedSerializer


class PinnedViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )
    serializer_class = CreatePinnedSerializer
    queryset = Pinned.objects.all().select_related(
        'event', 'article', 'event__company', 'created_by'
    ).prefetch_related(
        'target_groups', 'article__tags', 'event__pools', 'event__pools__registrations',
        'event__tags'
    )
    ordering = 'pinned_from'

    def get_serializer_class(self):
        if self.action == 'list':
            return ListPinnedSerializer
        return CreatePinnedSerializer
