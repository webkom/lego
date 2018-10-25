from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.pinned.models import Pinned
from lego.apps.pinned.serializers import (
    CreatePinnedSerializer, PinnedArticleSerializer, PinnedEventSerializer
)


class PinnedViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )
    serializer_class = CreatePinnedSerializer
    queryset = Pinned.objects.all()

    @list_route(methods=['GET'])
    def mine(self, request, pk=None):
        queryset_events = Pinned.objects.filter(
            target_groups__in=self.request.user.all_groups, pinned_from__lte=timezone.now(),
            pinned_to__gte=timezone.now()
        ).exclude(event__isnull=True).distinct()

        queryset_articles = Pinned.objects.filter(
            target_groups__in=self.request.user.all_groups, pinned_from__lte=timezone.now(),
            pinned_to__gte=timezone.now()
        ).exclude(article__isnull=True).distinct()

        events = PinnedEventSerializer(queryset_events, many=True).data
        articles = PinnedArticleSerializer(queryset_articles, many=True).data
        return Response({'pinned_events': events, 'pinned_articles': articles})
