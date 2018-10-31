from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.pinned.models import Pinned
from lego.apps.pinned.serializers import CreatePinnedSerializer, ListPinnedSerializer


class PinnedViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )
    serializer_class = CreatePinnedSerializer
    queryset = Pinned.objects.all()
    ordering = 'pinned_from'

    def get_serializer_class(self):
        if self.action == 'list':
            return ListPinnedSerializer
        return CreatePinnedSerializer
