from rest_framework import decorators, mixins, permissions, response, status, viewsets
from lego.utils.pagination import APIPagination
from .managers import NotificationFeedManager
from .serializers import AggregatedFeedSerializer, MarkSerializer
from .tasks import notifications_mark, notifications_mark_all


class NotificationFeedViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Actions:

    * /mark_all
    * /{id}/mark
    * /notification_data
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AggregatedFeedSerializer
    manager = NotificationFeedManager()
    pagination_class = [APIPagination]

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
        notifications_mark_all.delay(self.get_feed_key(), **data)
        return response.Response({}, status=status.HTTP_202_ACCEPTED)

    @decorators.detail_route(
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=MarkSerializer,
        methods=['POST']
    )
    def mark(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        notifications_mark.delay(self.get_feed_key(), pk, **data)
        return response.Response({}, status=status.HTTP_202_ACCEPTED)

    @decorators.list_route(
        permission_classes=[permissions.IsAuthenticated],
        methods=['GET']
    )
    def notification_data(self, request):
        feed = self.manager.get_feed(self.get_feed_key())
        return response.Response(feed.get_notification_data())
