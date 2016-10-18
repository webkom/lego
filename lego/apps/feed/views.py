from rest_framework import decorators, mixins, permissions, response, status, viewsets

from lego.apps.feed.feeds import NotificationFeed
from lego.utils.pagination import CursorPagination

from .managers import NotificationFeedManager
from .serializers import AggregatedFeedSerializer, MarkSerializer


class NotificationFeedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Actions:

    * /mark_all
    * /{id}/mark
    * /notification_data
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AggregatedFeedSerializer
    manager = NotificationFeedManager()
    filter_backends = []
    pagination_class = CursorPagination
    ordering = '-activity_id'

    def get_feed_key(self):
        return self.request.user.id

    def get_queryset(self):
        return self.manager.get_feed(self.get_feed_key())

    @decorators.list_route(
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=MarkSerializer,
        methods=['POST']
    )
    def mark_all(self, request):
        """
        This function marks all activities in a NotificationFeed as seen or/and red.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        feed = NotificationFeed(self.get_feed_key())
        feed.mark_all(**data)
        return response.Response({}, status=status.HTTP_200_OK)

    @decorators.detail_route(
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=MarkSerializer,
        methods=['POST']
    )
    def mark(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        feed = NotificationFeed(self.get_feed_key())
        feed.mark_activity(pk, **data)
        return response.Response({}, status=status.HTTP_200_OK)

    @decorators.list_route(
        permission_classes=[permissions.IsAuthenticated],
        methods=['GET']
    )
    def notification_data(self, request):
        feed = self.manager.get_feed(self.get_feed_key())
        return response.Response(feed.get_notification_data())
