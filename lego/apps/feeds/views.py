from rest_framework import decorators, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.feeds.attr_cache import AttrCache
from lego.apps.feeds.context import collect_refs

from .feed_manager import feed_manager
from .models import NotificationFeed, PersonalFeed, UserFeed
from .serializers.feeds import (
    AggregatedFeedSerializer,
    AggregatedMarkedFeedSerializer,
    MarkSerializer,
)


class FeedViewSet(viewsets.GenericViewSet):
    """
    Generic viewset base for all types of feeds.
    """

    ordering = "-updated_at"
    serializer_class = AggregatedFeedSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        data = list(page if page is not None else queryset)

        all_refs = set()
        for item in data:
            all_refs |= collect_refs(item)

        lookup = AttrCache().bulk_lookup(all_refs) if all_refs else {}

        serializer_context = self.get_serializer_context()
        serializer_context["attr_lookup"] = lookup

        if page is not None:
            serializer = self.get_serializer(
                data, many=True, context=serializer_context
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(data, many=True, context=serializer_context)
        return Response(serializer.data)


class FeedMarkerViewSet(viewsets.GenericViewSet):
    """
    Feed class with marker support
    """

    serializer_class = AggregatedMarkedFeedSerializer

    @decorators.action(detail=False, serializer_class=MarkSerializer, methods=["POST"])
    def mark_all(self, request):
        """
        This function marks all activities in a NotificationFeed as seen or/and red.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feed = self.get_queryset().model
        seen = serializer.validated_data["seen"]
        read = serializer.validated_data["read"]
        feed.mark_all(self.request.user.id, seen, read)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, serializer_class=MarkSerializer, methods=["POST"])
    def mark(self, request, pk):
        """
        Mark a single notification as read or seen.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feed = self.get_queryset().model
        seen = serializer.validated_data["seen"]
        read = serializer.validated_data["read"]
        feed.mark_all(self.request.user.id, str(pk), seen, read)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=["GET"])
    def notification_data(self, request):
        feed = self.get_queryset().model
        return Response(feed.get_notification_data(self.request.user.id))


class UserFeedViewSet(FeedViewSet):
    """
    Public events produced by users. This feed should not contain private information! This feed
    uses a url param to decide which feed to retrieve.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request is None:
            return UserFeed.objects.none()

        user_id = self.kwargs["user_pk"]
        return feed_manager.retrieve_feed(UserFeed, user_id)


class PersonalFeedViewSet(FeedViewSet):
    """
    Personal user timeline, based on request.user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request is None:
            return PersonalFeed.objects.none()

        return feed_manager.retrieve_feed(PersonalFeed, self.request.user.id)


class NotificationsViewSet(FeedMarkerViewSet, FeedViewSet):
    """
    Notifications feed based on request.user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request is None:
            return NotificationFeed.objects.none()

        return feed_manager.retrieve_feed(NotificationFeed, self.request.user.id)
