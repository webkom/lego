from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from lego.apps.articles.models import Article
from lego.apps.articles.serializers import PublicArticleSerializer
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.serializers.events import FrontpageEventSerializer
from lego.apps.permissions.constants import LIST
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.polls.models import Poll
from lego.apps.polls.serializers import DetailedPollSerializer
from lego.apps.users.models import User


class FrontpageViewSet(viewsets.ViewSet):

    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        cached_penalties = (
            self.request.user.number_of_penalties()
            if self.request.user.is_authenticated
            else None
        )

        def get_serializer_context():
            """
            Extra context provided to the serializer class.
            """
            return {
                "request": request,
                "format": self.format_kwarg,
                "view": self,
                "cached_penalties": cached_penalties,
            }

        articles_handler = get_permission_handler(Article)
        articles_queryset_base = (
            Article.objects.all()
            .order_by("-pinned", "-created_at")
            .prefetch_related("tags")
        )

        if articles_handler.has_perm(
            request.user, LIST, queryset=articles_queryset_base
        ):
            queryset_articles = articles_queryset_base
        else:
            queryset_articles = articles_handler.filter_queryset(
                request.user, articles_queryset_base
            )

        events_handler = get_permission_handler(Event)
        queryset_events_base = (
            Event.objects.all()
            .filter(end_time__gt=timezone.now())
            .order_by("-pinned", "start_time", "id")
            .prefetch_related("pools", "pools__registrations", "company", "tags")
        )
        if request.user.is_authenticated:
            queryset_events_base = queryset_events_base.prefetch_related(
                "pools__registrations__user",
                Prefetch(
                    "registrations",
                    queryset=Registration.objects.filter(user=request.user),
                    to_attr="user_reg",
                ),
                Prefetch(
                    "pools",
                    queryset=Pool.objects.filter(
                        permission_groups__in=self.request.user.all_groups
                    ),
                    to_attr="possible_pools",
                ),
            )

        if events_handler.has_perm(request.user, LIST, queryset=queryset_events_base):
            queryset_events = queryset_events_base
        else:
            queryset_events = events_handler.filter_queryset(
                request.user, queryset_events_base
            )

        queryset_poll = Poll.objects.filter(pinned=True).order_by("created_at").last()

        articles = PublicArticleSerializer(
            queryset_articles[:10], context=get_serializer_context(), many=True
        ).data
        events = FrontpageEventSerializer(
            queryset_events, context=get_serializer_context(), many=True
        ).data
        poll = (
            DetailedPollSerializer(queryset_poll, context=get_serializer_context()).data
            if queryset_poll
            else None
        )
        ret = {"articles": articles, "events": events, "poll": poll}

        return Response(ret)
