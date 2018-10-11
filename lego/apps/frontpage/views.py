from django.utils import timezone
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

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def list(self, request):
        articles_handler = get_permission_handler(Article)
        articles_queryset_base = Article.objects.all()\
            .order_by('-pinned', '-created_at').prefetch_related('tags')

        if articles_handler.has_perm(request.user, LIST, queryset=articles_queryset_base):
            queryset_articles = articles_queryset_base
        else:
            queryset_articles = articles_handler.filter_queryset(
                request.user, articles_queryset_base
            )

        events_handler = get_permission_handler(Event)
        queryset_events_base = Event.objects.all()\
            .filter(end_time__gt=timezone.now()).order_by('-pinned', 'start_time', 'id')\
            .prefetch_related('pools', 'pools__registrations', 'company', 'tags')

        if events_handler.has_perm(request.user, LIST, queryset=queryset_events_base):
            queryset_events = queryset_events_base
        else:
            queryset_events = events_handler.filter_queryset(request.user, queryset_events_base)

        articles = PublicArticleSerializer(
            queryset_articles[:10], context=self.get_serializer_context(), many=True
        ).data
        events = EventSearchSerializer(
            queryset_events, context=self.get_serializer_context(), many=True
        ).data
        ret = {
            'articles': articles,
            'events': events,
        }

        return Response(ret)
