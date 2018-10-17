from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.pinned.models import PinnedArticle, PinnedEvent
from lego.apps.pinned.serializers import (
    CreatePinnedArticleSerializer, CreatePinnedEventSerializer, PinnedArticleSerializer,
    PinnedEventSerializer
)


class PinnedViewSet(AllowedPermissionsMixin, viewsets.ViewSet):

    permission_classes = (IsAuthenticated, )

    def list(self, request):
        queryset_events = PinnedEvent.objects.filter(
            target_groups__in=self.request.user.all_groups, pinned_from__lte=timezone.now(),
            pinned_to__gte=timezone.now()
        ).distinct()

        queryset_articles = PinnedArticle.objects.filter(
            target_groups__in=self.request.user.all_groups, pinned_from__lte=timezone.now(),
            pinned_to__gte=timezone.now()
        ).distinct()

        events = PinnedEventSerializer(queryset_events, many=True).data
        articles = PinnedArticleSerializer(queryset_articles, many=True).data
        return Response({'pinned_events': events, 'pinned_articles': articles})

    @list_route(methods=['GET'])
    def all(self, request, pk=None):
        queryset_events = PinnedEvent.objects.all()

        queryset_articles = PinnedArticle.objects.all()

        events = PinnedEventSerializer(queryset_events, many=True).data
        articles = PinnedArticleSerializer(queryset_articles, many=True).data
        return Response({'pinned_events': events, 'pinned_articles': articles})

    @list_route(methods=['POST'])
    def pin_event(self, request, pk=None):
        serializer = CreatePinnedEventSerializer(
            data=request.data, context={
                'request': self.request,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @list_route(methods=['POST'])
    def pin_article(self, request, pk=None):
        serializer = CreatePinnedArticleSerializer(
            data=request.data, context={
                'request': self.request,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
