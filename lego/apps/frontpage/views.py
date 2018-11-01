from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.permissions.constants import LIST
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.pinned.models import Pinned
from lego.apps.pinned.serializers import FrontpagePinnedSerializer


class FrontpageViewSet(viewsets.ViewSet):

    permission_classes = (permissions.AllowAny, )

    def list(self, request):
        queryset_pinned = Pinned.objects.filter(
            pinned_from__lte=timezone.now(),
            pinned_to__gte=timezone.now(),
            target_groups__in=self.request.user.all_groups,
        ).distinct()

        queryset_pinned_events = queryset_pinned.exclude(
            event__isnull=True
        ).order_by('pinned_from').select_related('event', 'event__company').prefetch_related(
            'event__pools', 'event__pools__registrations', 'event__tags'
        )

        queryset_pinned_articles = queryset_pinned.exclude(
            article__isnull=True
        ).order_by('pinned_from').select_related('article').prefetch_related('article__tags')

        pinned_events = FrontpagePinnedSerializer(queryset_pinned_events, many=True).data
        pinned_articles = FrontpagePinnedSerializer(queryset_pinned_articles, many=True).data

        articles_handler = get_permission_handler(Article)
        articles_queryset_base = Article.objects.all()\
            .order_by('-created_at').prefetch_related('tags')

        if articles_handler.has_perm(request.user, LIST, queryset=articles_queryset_base):
            queryset_articles = articles_queryset_base
        else:
            queryset_articles = articles_handler.filter_queryset(
                request.user, articles_queryset_base
            )

        events_handler = get_permission_handler(Event)
        queryset_events_base = Event.objects.all()\
            .filter(end_time__gt=timezone.now()).order_by('start_time', 'id')\
            .prefetch_related('pools', 'pools__registrations', 'company', 'tags')

        if events_handler.has_perm(request.user, LIST, queryset=queryset_events_base):
            queryset_events = queryset_events_base
        else:
            queryset_events = events_handler.filter_queryset(request.user, queryset_events_base)

        articles = PublicArticleSerializer(queryset_articles[:10], many=True).data
        events = EventSearchSerializer(queryset_events, many=True).data
        ret = {
            'pinned_articles': pinned_articles,
            'pinned_events': pinned_events,
            'articles': articles,
            'events': events,
        }

        return Response(ret)
