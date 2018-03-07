from rest_framework import decorators, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.feeds.attr_cache import AttrCache

from .feed_manager import feed_manager
from .models import NotificationFeed, PersonalFeed, UserFeed
from .serializers import AggregatedFeedSerializer, AggregatedMarkedFeedSerializer, MarkSerializer


class FeedViewSet(viewsets.GenericViewSet):
    """
    Generic viewset base for all types of feeds.
    """

    ordering = '-activity_id'
    serializer_class = AggregatedFeedSerializer

    def attach_metadata(self, data):
        """
        Map over the feed here to attach more information to each element.
        """
        content_strings = set()

        for item in data:
            activities = item.get('activities')
            if activities:
                # Aggregated Activity
                for activity in activities:
                    target = activity.get('target')
                    object = activity.get('object')
                    actor = activity.get('actor')
                    content_strings.add(target) if target else None
                    content_strings.add(object) if object else None
                    content_strings.add(actor) if actor else None

        if content_strings:
            cache = AttrCache()
            lookup = cache.bulk_lookup(content_strings)

        for item in data:
            context = {}

            activities = item.get('activities')
            if activities:
                # Aggregated Activity
                for activity in activities:
                    target = activity.get('target')
                    object = activity.get('object')
                    actor = activity.get('actor')
                    if target in lookup.keys():
                        context[target] = lookup[target]
                    if object in lookup.keys():
                        context[object] = lookup[object]
                    if actor in lookup.keys():
                        context[actor] = lookup[actor]
            item['context'] = context

        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.attach_metadata(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(self.attach_metadata(serializer.data))


class FeedMarkerViewSet(viewsets.GenericViewSet):
    """
    Feed class with marker support
    """

    serializer_class = AggregatedMarkedFeedSerializer

    @decorators.list_route(serializer_class=MarkSerializer, methods=['POST'])
    def mark_all(self, request):
        """
        This function marks all activities in a NotificationFeed as seen or/and red.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.detail_route(serializer_class=MarkSerializer, methods=['POST'])
    def mark(self, request, pk):
        """
        Mark a single notification as read or seen.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.list_route(methods=['GET'])
    def notification_data(self, request):
        feed = self.get_queryset().model
        return Response(feed.get_notification_data('1'))


class UserFeedViewSet(FeedViewSet):
    """
    Public events produced by users. This feed should not contain private information! This feed
    uses a url param to decide which feed to retrieve.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_pk']
        return feed_manager.retrieve_feed(UserFeed, user_id)


class PersonalFeedViewSet(FeedViewSet):
    """
    Personal user timeline, based on request.user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return feed_manager.retrieve_feed(PersonalFeed, self.request.user.id)


class NotificationsViewSet(FeedViewSet, FeedMarkerViewSet):
    """
    Notifications feed based on request.user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return feed_manager.retrieve_feed(NotificationFeed, self.request.user.id)
