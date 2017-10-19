from rest_framework import viewsets, serializers
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import SearchArticleSerializer
from lego.apps.events.models import Event
from lego.apps.events.serializers.events import EventSearchSerializer


class FrontpageViewSet(viewsets.ViewSet):

    def list(self, _request):
        # TODO: filter out old events
        # note that articles will be old, but events are 'new', in the sense
        # that the start time hasn't passed yet.
        queryset_articles = Article.objects.all().order_by('pinned', 'created_at')
        queryset_events = Event.objects.all().order_by('pinned', 'start_time')
        articles = SearchArticleSerializer(queryset_articles, many=True).data
        events = EventSearchSerializer(queryset_events, many=True).data
        ret = {
            'articles': articles,
            'events': events,
        }
        return Response(ret)
