from django.utils.datetime_safe import datetime
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventSearchSerializer
from lego.apps.permissions.constants import LIST
from lego.apps.permissions.utils import get_permission_handler


class FrontpageViewSet(viewsets.ViewSet):

    permission_classes = (permissions.AllowAny, )

    def list(self, request):
        articles_handler = get_permission_handler(Article)
        articles_queryset_base = Article.objects.all()\
            .order_by('pinned', '-created_at').prefetch_related('tags')

        if articles_handler.has_perm(request.user, LIST, queryset=articles_queryset_base):
            queryset_articles = articles_queryset_base
        else:
            queryset_articles = articles_handler.filter_queryset(
                request.user, articles_queryset_base
            )

        events_handler = get_permission_handler(Event)
        queryset_events_base = Event.objects.all()\
            .filter(start_time__gt=datetime.now()).order_by('pinned', 'start_time')\
            .prefetch_related('pools', 'pools__registrations', 'company', 'tags')

        if events_handler.has_perm(request.user, LIST, queryset=queryset_events_base):
            queryset_events = queryset_events_base
        else:
            queryset_events = events_handler.filter_queryset(request.user, queryset_events_base)

        articles = PublicArticleSerializer(queryset_articles[:10], many=True).data
        events = EventSearchSerializer(queryset_events, many=True).data
        ret = {
            'articles': articles,
            'events': events,
        }

        return Response(ret)
